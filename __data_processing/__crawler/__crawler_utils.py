"""
Utility Functions for Web Crawling and Text Processing:
1. Manage proxy usage for HTTP requests.
2. Extract keywords from JSON files or strings.
3. Perform HTTP requests with retry and proxy support.
4. Filter and clean HTML content using BeautifulSoup.
5. Identify product-related patterns in strings.
"""

import json
import requests
import re
from bs4 import BeautifulSoup

# Proxy pool service URL
PROXY_POOL_URL = 'http://127.0.0.1:5010'


def get_proxy():
    """
    Fetch a proxy from the proxy pool.
    Returns:
        str: Proxy string if successful, otherwise None.
    """
    try:
        response = requests.get(PROXY_POOL_URL)
        if response.status_code == 200:
            return response.text
    except ConnectionError:
        return None


def delete_proxy(proxy):
    """
    Remove a proxy from the proxy pool.
    Args:
        proxy (str): Proxy to delete.
    """
    requests.get(f"http://127.0.0.1:5010/delete/?proxy={proxy}")


def load_keywords_from_tfidf(json_file_path: str = None, json_str: str = None):
    """
    Load keywords identified by TF-IDF from a JSON file or JSON string.
    Args:
        json_file_path (str): Path to the JSON file containing keywords.
        json_str (str): JSON string containing keywords.
    Returns:
        list: A list of unique keyword sets.
    """
    if json_file_path:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    elif json_str:
        data = json.loads(json_str)
    else:
        raise ValueError("Either json_file_path or json_str must be provided.")

    keywords = []
    for item in data.values():
        if item not in keywords:
            keywords.append(item)

    return keywords


def common_request(search_url, retry_count: int = 5):
    """
    Perform an HTTP GET request with retry and proxy support.
    Args:
        search_url (str): The URL to fetch.
        retry_count (int): Number of retry attempts (default: 5).
    Returns:
        str: Response text if successful, otherwise None.
    """
    search_results = None

    # Proxy settings
    tunnel = "tunnel"
    username = "username"
    password = "password"
    proxies = {
        "http": f"http://{username}:{password}@{tunnel}/",
        "https": f"http://{username}:{password}@{tunnel}/"
    }

    while retry_count > 0:
        try:
            response = requests.get(search_url, proxies=proxies)
            if response.status_code == 200 and response.text:
                search_results = response.text
                break
            else:
                retry_count -= 1
        except Exception as e:
            print(f"Error fetching URL: {e}")
            retry_count -= 1

    return search_results


def word_product_re_pattern(ori_word):
    """
    Identify product-related patterns in a given word.
    Args:
        ori_word (str): The word to match against patterns.
    Returns:
        str: The original word if a pattern match is found, otherwise None.
    """
    text = f" {ori_word} "
    pattern_num_cha = r'(?=.*\d)(?=.*[a-zA-Z])'
    pattern1 = r' [a-zA-Z0-9]+-[a-zA-Z0-9]+ '
    pattern2 = r' [a-zA-Z]+[0-9]+ '

    matches1 = re.findall(pattern1, text)
    matches2 = re.findall(pattern2, text)

    if matches1 and re.search(pattern_num_cha, matches1[0]):
        return ori_word
    elif matches2:
        return ori_word


def crawler_html_filter(link, html_content):
    """
    Filter and clean HTML content to extract title and text information.
    Args:
        link (str): The URI of the webpage.
        html_content (str): The raw HTML content of the page.
    Returns:
        dict: A dictionary containing the URI, title, and cleaned text.
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract title
    title = soup.title.string if soup.title else 'No title found'

    # Extract and clean text
    text = soup.get_text()
    cleaned_text = ' '.join(text.split())

    return {
        "uri": link,
        "title": title,
        "web_info": cleaned_text
    }
