"""
File Save Utilities:
1. Save string content to a file.
2. Save dictionary content to a JSON file.
3. Save list content to a CSV file.
"""

import os
import json
import csv


def save_str_file(file_path: str, str_content: str):
    """
    Save string content to a specified file.
    Creates the directory if it doesn't exist.
    Args:
        file_path (str): The path to save the file.
        str_content (str): The string content to save.
    """
    try:
        # Ensure the directory exists
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Save the string content to the file
        with open(file_path, 'w', encoding="utf-8") as file:
            file.write(str_content)
        print(f"File has been saved to {file_path}")
    except Exception as e:
        print(f"Error saving file: {e}")


def save_dict_to_json(file_path: str, dict_content: dict):
    """
    Save dictionary content to a JSON file.
    Creates the directory if it doesn't exist.
    Args:
        file_path (str): The path to save the JSON file.
        dict_content (dict): The dictionary content to save.
    """
    try:
        # Ensure the directory exists
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Save the dictionary as a JSON file
        with open(file_path, 'w', encoding="utf-8") as file:
            json.dump(dict_content, file, indent=4, ensure_ascii=False)
        print(f"JSON file has been saved to {file_path}")
    except Exception as e:
        print(f"Error saving JSON file: {e}")


def save_list_to_csv(file_path: str, data_list: list):
    """
    Save list content to a CSV file.
    The first row of the list is considered as the header.
    Args:
        file_path (str): The path to save the CSV file.
        data_list (list): A 2D list where the first row is the header.
    Example:
        data_list = [
            ['Name', 'Age', 'Gender'],
            ['John', 25, 'Male'],
            ['Jane', 30, 'Female'],
            ['Alice', 28, 'Female'],
        ]
    """
    try:
        # Ensure the directory exists
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Save the list to a CSV file
        with open(file_path, 'w', newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerows(data_list)
        print(f"CSV file has been saved to {file_path}")
    except Exception as e:
        print(f"Error saving CSV file: {e}")
