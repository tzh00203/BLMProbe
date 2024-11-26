"""
Data Sanitization and Filtering for Response Data:
1. Load raw response data.
2. Apply sanitization rules to filter and clean the data.
3. Save the sanitized data to a JSON file.
"""

import re
import json
from __utils.__path_util import global_path
from __utils.__save_file_util import save_dict_to_json
from __utils.__unicode_util import unicode_filter
from __utils.__filter_util import html_filter, filter_dictionary_string


# Global Paths
ROOT_PATH = global_path.__2_response_pattern_result_path__
RAW_DATA_PATH = global_path.__text_path__
OUTPUT_PATH = global_path.__raw_data_path__ + "all_response_sanitization_v3.json"


def extract_status_code(response_text: str) -> str:
    """
    Extract HTTP status code from the response text.
    :param response_text: Raw HTTP response string.
    :return: Status code if found, else None.
    """
    match = re.match(r"HTTP/1\.1 (\d+) ", response_text)
    return match.group(1) if match else None


def sanitization_string(response_text: str) -> str:
    """
    Apply sanitization rules to clean and filter a response string.
    :param response_text: The raw response string.
    :return: Sanitized string or an empty string if filtering conditions are met.
    """
    if not response_text:
        return ""

    # Filter HTTP/HTTPS responses
    if response_text.startswith("HTTP/"):
        status_code = extract_status_code(response_text)
        if status_code and status_code.startswith(('3', '5')):
            print("\tFiltered: Bad HTTP status code.")
            return ""
        response_text = html_filter(response_text)

    # Apply generic filters
    response_text = unicode_filter(response_text)
    response_text = re.sub(r"<\s*p\s*>(.*?)<\s*/\s*p\s*>", " ", response_text)
    response_text = re.sub(r"\\x[0-9a-fA-F]{2}", " ", response_text)  # Remove hex sequences
    response_text = re.sub(r"x[0-9a-fA-F]{2}", " ", response_text)  # Remove hex sequences
    response_text = re.sub(r"\s+", " ", response_text)  # Collapse multiple spaces
    response_text = re.sub(r"-+", "-", response_text)  # Collapse multiple hyphens

    # Handle edge cases for '.' symbol
    response_text = re.sub(r"\.+", ".", response_text)
    response_text = re.sub(r"\s*\.\s", " ", response_text)
    response_text = re.sub(r"\s\.\s*", " ", response_text)
    response_text = re.sub(r"\s*\.$", " ", response_text)
    response_text = re.sub(r"^\.\s*", " ", response_text)

    # Remove single-character strings and stop words
    response_text = ' '.join([word for word in response_text.strip().split() if len(word) > 1])
    response_text = response_text.lower()
    response_text = filter_dictionary_string(response_text)

    return response_text


def load_data():
    """
    Load raw response data, sanitize it, and save the sanitized data.
    """
    try:
        # Load raw data
        with open(RAW_DATA_PATH, "r", encoding="utf-8") as raw_file:
            raw_data = json.load(raw_file)

        raw_data_list = raw_data.get("natural language", [])
        result_dict = {"sanitization_data": []}

        # Process and sanitize each response string
        for idx, response in enumerate(raw_data_list, start=1):
            print(f"Processing line {idx}...")
            sanitized_data = sanitization_string(response)
            if sanitized_data:
                result_dict["sanitization_data"].append(sanitized_data)

        # Save sanitized data
        save_dict_to_json(OUTPUT_PATH, result_dict)
        print(f"Sanitized data saved to {OUTPUT_PATH}")
        return result_dict

    except Exception as e:
        print(f"Error occurred during data processing: {e}")


if __name__ == "__main__":
    load_data()
