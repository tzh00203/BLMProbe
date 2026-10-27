import json
import os, re, sys
import requests
from multiprocessing import Process
from pathlib import Path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from __utils.__save_file_util import save_dict_to_json
from __logs.__log import log_init
from __utils.__path_util import global_path
from __crawler.__crawler_utils import crawler_html_filter, common_request
from __agent_utils import truncate_chat_messages, LLMCaller
from __agent_config import *
import time

class BingExploringAgent:
    """
    Bing Exploring Agent for concurrent crawling, webpage sanitization,
    and IoT-related attribute extraction using OpenAI API.
    """
    def __init__(self, mode="gpt"):
        self.result_path = global_path.__crawler_search_result_path__
        self.logger_dir = f"{self.result_path}webpage_log/"
        self.api_key = bing_exploring_agent_api_key

    '''
    def openai_api_request(self, user_input):
        """
        Use OpenAI API to extract IoT-related attributes from webpage data.
        Args:
            user_input (dict): Dictionary containing webpage {uri, title, web_info}.
        Returns:
            dict: Extracted attributes {vendor, type, product, device_description}.
        """
        message = [
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

        try:
            response = self.caller._send_request_to_llm(message=message)
            result = json.loads(response)
            openai_labels_dict = eval(result["choices"][0]["message"]["content"])
            self.logger.info(f"Get OpenAI API results: {openai_labels_dict}")
            return openai_labels_dict
        except Exception as e:
            self.logger.error(f"OpenAI API request failed: {e}")
            return {"vendor": "null", "type": "null", "product": "null", "device_description": "null"}
    '''
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
                        You are a WEB page entity name extractor. The user will input the basic information of the WEB page 
                        related (including the uri link of the web page, the title of the page, and the text 
                        information of the page). You need to determine whether the information input by the user is related to a 
                        certain network device. The output information contains three dimensions: device vendor name, device 
                        type, device model information
                
                            User input: dictionary type {uri, title, web_info}
                            Your answer output format:
                            {'vendor': '', 'type': '', 'product': '', 'device_description': ''}
                            Attention:
                            1. If the vendor or device type is unknown, the attribute value is "null".
                            2. The extracted attribute value must come from the attribute value in the dictionary information ({uri, title, web_info}) input by the user
                            3. If the input information does not contain network device information, the attribute value corresponding to each attribute in the dictionary is null. (The vendor and type are irrelevant to the network device.)
                            4. If the model information is displayed, determine whether to describe the device based on the context. If more than one series name or model number is included and cannot be determined to be unique, the product property value is empty.
                            5. The 'device_description' is used to extract the definition and functionality of the device from this web page
                            6. Your answer only needs to be given a dictionary of results and does not need to contain additional strings
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
                self.logger.info(f"Get OpenAI API results: {openai_labels_dict}")
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

    def process_webpages(self, uri_lines, uri_lists, start_idx, end_idx):
        """
        Process a subset of URIs, fetch webpage content, sanitize, and make OpenAI requests.
        Args:
            uri_lines (list): List of sanitization line indices.
            uri_lists (list): List of URI lists.
            start_idx (int): Start index for processing.
            end_idx (int): End index for processing.
            shared_results (multiprocessing.Manager.dict): Shared dictionary to store OpenAI labels.
        """
        logger_path = Path(self.logger_dir, f"webpage_uri_{start_idx}_{end_idx}.log")
        sanitization_json_path = Path(self.logger_dir, f"webpage_sanitization_{start_idx}_{end_idx}.json")
        logger = log_init(log_filename=str(logger_path))
        local_results = {}

        for count, (line, uris) in enumerate(zip(uri_lines[start_idx:end_idx + 1], uri_lists[start_idx:end_idx + 1]), 1):
            logger.info(f"Processing line {line} ({count}/{end_idx - start_idx + 1})")

            processed_count = 0
            for uri in uris:  # Limit to the first 5 URIs
                if uri.lower().endswith(".pdf"):
                    continue
                response_html = common_request(uri)
                sanitization_entry = {
                    "uri": uri,
                    "title": "null",
                    "web_info": "null"
                }

                if response_html:
                    logger.info(f"Successfully fetched {uri}")
                    sanitization_entry = crawler_html_filter(uri, response_html)

                    # Make OpenAI API request for label extraction
                    openai_labels = self.openai_api_request(sanitization_entry)
                    time.sleep(0.6)
                    sanitization_entry["openai_labels"] = openai_labels
                else:
                    logger.error(f"Failed to fetch {uri}")
                    sanitization_entry["openai_labels"] = {"vendor": "null", "type": "null", "product": "null", "device_description": "null"}

                # Store results locally
                sanitization_entry.pop("web_info", None)
                
                local_results.setdefault(line, []).append(sanitization_entry)
                processed_count += 1
                if processed_count >= 5:
                    break
        
        # Save sanitization results to disk
        save_dict_to_json(sanitization_json_path, local_results)
        logger.info(f"Sanitization and OpenAI request completed. Results saved to {sanitization_json_path}")

    def run(self):
        """
        Main function to load URI logs, process data concurrently, and make OpenAI requests.
        Outputs:
            dict: A dictionary containing the sanitized data and the OpenAI-extracted labels.
        """
        self.logger = log_init(f"{global_path.__crawler_search_result_path__}search_log/bing_exploring_agent.log")
        # for filename in os.listdir(self.logger_dir):
        #     os.remove(self.logger_dir + filename)
        uri_log_path = Path(self.result_path, "search_log")
        # uri_log_path = Path("./")
        uri_pattern = r"Line:\s+(\d+).*?URI:\s+([^\s]+(?:\s+[^\s]+)*)"

        webpage_uri_dict = {}
        # for subdir in Path(self.result_path).iterdir():
        #     if subdir.is_dir() and subdir.name.startswith("search_log_part"):
        # # 遍历该子目录中的所有文件
        #         for log_file in subdir.iterdir():
        # Load URI logs
        for log_file in uri_log_path.iterdir():
            if not str(log_file).split("/")[-1].startswith("search_uri"):
                continue
            lines = log_file.read_text(encoding="utf-8").splitlines()
            for line in lines:
                match = re.search(uri_pattern, line)
                if match:
                    line_str, uri = match.groups()
                    webpage_uri_dict.setdefault(line_str, []).append(uri)
                    webpage_uri_dict[line_str] = list(set(webpage_uri_dict[line_str]))
        uri_lines, uri_lists = list(webpage_uri_dict.keys()), list(webpage_uri_dict.values())
        total_uris = len(uri_lines)
        save_dict_to_json(global_path.__raw_data_path__+"/raw_data/tmp_line_index_url.json", webpage_uri_dict)
      
        num_processes = PROCESS_COUNt
        chunk_size = total_uris // num_processes

        # Concurrent processing
        processes = []
        for i in range(num_processes):
            start_idx = i * chunk_size
            end_idx = (i + 1) * chunk_size - 1 if i < num_processes - 1 else total_uris - 1
            process = Process(
                target=self.process_webpages,
                args=(uri_lines, uri_lists, start_idx, end_idx)
            )
            processes.append(process)
            process.start()
        
        for process in processes:
            process.join()

        self.logger.info("All processes completed successfully.")

if __name__ == "__main__":
    # agent = BingExploringAgent()
    # agent.run()
    bing_agent = BingExploringAgent()
    print(bing_agent.openai_api_request("""
                                        {uri: http://www.dlink.com/product?p=dir-816l, title:"null", web_info: null}
                                        """))
