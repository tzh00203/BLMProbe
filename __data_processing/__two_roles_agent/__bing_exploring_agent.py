import json
import os, re
import requests
from multiprocessing import Process
from pathlib import Path
from __utils.__save_file_util import save_dict_to_json
from __logs.__log import log_init
from __utils.__path_util import global_path
from __crawler.__crawler_utils import crawler_html_filter
from BLMProbe.__data_processing.__two_roles_agent.__agent_utils import truncate_chat_messages

class BingExploringAgent:
    """
    Bing Exploring Agent for concurrent crawling, webpage sanitization,
    and IoT-related attribute extraction using OpenAI API.
    """

    def __init__(self, api_key):
        self.logger = log_init("bing_exploring_agent.log")
        self.result_path = global_path.__crawler_search_result_path__
        self.api_key = api_key

    def openai_api_request(self, user_input):
        """
        Use OpenAI API to extract IoT-related attributes from webpage data.
        Args:
            user_input (dict): Dictionary containing webpage {uri, title, web_info}.
        Returns:
            dict: Extracted attributes {vendor, type, product, device_description}.
        """
        url = 'https://api.openai.com/v1/chat/completions'

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}',
        }

        data = {
            "model": "gpt-4o-mini",
            "temperature": 0.2,
            "messages": [
                {
                    "role": "system",
                    "content": """
                        Given user input {uri, title, web_info}, determine if it pertains to an
                        Internet-connected device, and extract device attributes.
                        Output format: { 'vendor': ' ', 'type': ' ', 'product': ' ', 'device description': ' '} 
                    """
                },
                {
                    "role": "user",
                    "content": f"user input: {user_input}",
                }
            ]
        }
        max_tokens = 4096

        truncated_messages = truncate_chat_messages(data["messages"], max_tokens, data["model"])
        data["messages"] = truncated_messages

        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            if response.status_code == 200:
                result = response.json()
                openai_labels_dict = eval(result["choices"][0]["message"]["content"])
                return openai_labels_dict
            else:
                self.logger.error(f"OpenAI API error: {response.status_code}")
                return {"vendor": "null", "type": "null", "product": "null", "device_description": "null"}
        except Exception as e:
            self.logger.error(f"OpenAI API request failed: {e}")
            return {"vendor": "null", "type": "null", "product": "null", "device_description": "null"}

    def sanitize_and_extract(self, uri, response_html):
        """
        Sanitize webpage content and use OpenAI API to extract attributes.
        Args:
            uri (str): Webpage URI.
            response_html (str): HTML content of the webpage.
        Returns:
            dict: Extracted attributes with sanitization.
        """
        try:
            sanitized_data = crawler_html_filter(uri, response_html)
            attributes = self.openai_api_request(sanitized_data)
            return {"uri": uri, **attributes}
        except Exception as e:
            self.logger.error(f"Error sanitizing or extracting from {uri}: {e}")
            return {"uri": uri, "vendor": "null", "type": "null", "product": "null"}

    def process_webpages(self, uri_lines, uri_lists, start_idx, end_idx, shared_results):
        """
        Process a subset of URIs, fetch webpage content, sanitize, and make OpenAI requests.
        Args:
            uri_lines (list): List of sanitization line indices.
            uri_lists (list): List of URI lists.
            start_idx (int): Start index for processing.
            end_idx (int): End index for processing.
            shared_results (multiprocessing.Manager.dict): Shared dictionary to store OpenAI labels.
        """
        logger_path = Path(self.result_path, f"webpage_log/webpage_uri_{start_idx}_{end_idx}.log")
        sanitization_json_path = Path(self.result_path, f"webpage_log/webpage_sanitization_{start_idx}_{end_idx}.json")
        logger = log_init(logFilename=str(logger_path))
        local_results = {}

        for count, (line, uris) in enumerate(zip(uri_lines[start_idx:end_idx + 1], uri_lists[start_idx:end_idx + 1]), 1):
            logger.info(f"Processing line {line} ({count}/{end_idx - start_idx + 1})")

            for uri in uris[:5]:  # Limit to the first 5 URIs
                response_html = self.common_request(uri)
                sanitization_entry = {
                    "uri": uri,
                    "title": "null",
                    "web_info": "null"
                }

                if response_html:
                    logger.info(f"Successfully fetched {uri}")
                    sanitization_entry = self.crawler_html_filter(uri, response_html)

                    # Make OpenAI API request for label extraction
                    openai_labels = self.make_openai_request(sanitization_entry)
                    sanitization_entry["openai_labels"] = openai_labels
                else:
                    logger.error(f"Failed to fetch {uri}")
                    sanitization_entry["openai_labels"] = {"vendor": "null", "type": "null", "product": "null"}

                # Store results locally
                local_results.setdefault(line, []).append(sanitization_entry)

        # Save sanitization results to disk
        save_dict_to_json(sanitization_json_path, local_results)
        logger.info(f"Sanitization and OpenAI request completed. Results saved to {sanitization_json_path}")

        # Update shared_results dictionary
        shared_results.update(local_results)

    def run(self):
        """
        Main function to load URI logs, process data concurrently, and make OpenAI requests.
        Outputs:
            dict: A dictionary containing the sanitized data and the OpenAI-extracted labels.
        """
        uri_log_path = Path(self.result_path, "search_log")
        uri_pattern = r"INFO\s+(\S+)\s+line.*?:search\s+uri:\s+(\S+)"
        webpage_uri_dict = {}

        # Load URI logs
        for log_file in uri_log_path.iterdir():
            lines = log_file.read_text(encoding="utf-8").splitlines()
            for line in lines:
                match = re.search(uri_pattern, line)
                if match:
                    line_str, uri = match.groups()
                    webpage_uri_dict.setdefault(line_str, []).append(uri)

        uri_lines, uri_lists = list(webpage_uri_dict.keys()), list(webpage_uri_dict.values())
        total_uris = len(uri_lines)
        num_processes = 10
        chunk_size = total_uris // num_processes

        # Shared dictionary to collect OpenAI labels
        from multiprocessing import Manager
        manager = Manager()
        shared_results = manager.dict()

        # Concurrent processing
        processes = []
        for i in range(num_processes):
            start_idx = i * chunk_size
            end_idx = (i + 1) * chunk_size - 1 if i < num_processes - 1 else total_uris - 1
            process = Process(
                target=self.process_webpages,
                args=(uri_lines, uri_lists, start_idx, end_idx, shared_results)
            )
            processes.append(process)
            process.start()

        for process in processes:
            process.join()

        self.logger.info("All processes completed successfully.")

        # Convert shared_results to a regular dictionary
        final_results = dict(shared_results)
        return final_results


if __name__ == "__main__":
    agent = BingExploringAgent()
    agent.run()
