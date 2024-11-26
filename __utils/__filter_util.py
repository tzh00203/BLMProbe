"""
Text and HTML Filtering Utilities:
1. Clean and filter text data based on pre-defined rules.
2. Extract meaningful content from HTML strings.
"""

import re
from bs4 import BeautifulSoup
from __path_util.utils_path import WORD_DICTIONARY_PATH, BLACKLIST_PATH

# ========================= Filter Lists =========================

# Symbols to be removed or replaced in text
FORMAT_SYMBOLS = [
    "\r", "\n", ": ", ". ", ", ", ";", "!", "=", " -", "\'"
]

# HTTP headers to filter from HTML content
HTTP_FILTER_LIST = [
    "HTTP/", "Date:", "Content-Type:", "Content-Length:", "Last-Modified:", "Accept-Ranges:",
    "Content-Security-Policy:", "X-Content-Type-Options:", "x-xss-protection:", "Expires:", "Cache-Control:",
    "Pragma:", "Vary:", "Connection:", "Strict-Transport-Security:"
]

# HTML tags to remove during cleaning
HTML_TAGS_TO_REMOVE = ['<link>', '<script>', '<style>', '</html>', '</body>']

# Prepare dictionary and blacklist
with open(WORD_DICTIONARY_PATH, "r", encoding="utf-8") as f:
    DICTIONARY_WORDS_LIST = f.read().replace(" ", "").split("\n")

with open(BLACKLIST_PATH, "r", encoding="utf-8") as f:
    BLACKLIST = f.read().split(',')


def filter_format_symbol(text: str) -> str:
    """
    Remove or replace specific symbols from the text.
    Args:
        text (str): The input text to clean.
    Returns:
        str: The cleaned text.
    """
    for symbol in FORMAT_SYMBOLS:
        text = text.replace(symbol, " ")
    
    # Remove numeric-only parts
    text = re.sub(r' \d+ ', ' ', text)
    
    # Normalize whitespace and convert to lowercase
    return re.sub(r'\s+', ' ', text).lower()


def filter_chinese(text: str) -> str:
    """
    Remove Chinese characters from the text.
    Args:
        text (str): The input text.
    Returns:
        str: The text without Chinese characters.
    """
    return re.sub(r"[\u4e00-\u9fff]+", '', text)


def filter_non_ascii(text: str) -> str:
    """
    Remove non-ASCII characters from the text.
    Args:
        text (str): The input text.
    Returns:
        str: The text with only ASCII characters.
    """
    return re.sub(r'[^\x00-\x7F]+', ' ', text)


def filter_keyword_list_string(keyword_list: list, ori_string: str) -> list:
    """
    Filter keywords from a string based on similarity with a provided list.
    Args:
        keyword_list (list): List of reference keywords.
        ori_string (str): Original input string.
    Returns:
        list: List of matching keywords with high similarity.
    """
    from __utils.__similarity_util import similarity

    result_word_list = []
    string_words_list = ori_string.strip().split()

    for string_word in string_words_list:
        for key_word in keyword_list:
            _, similarity_value = similarity(string_word, key_word)
            if similarity_value > 0.90:
                result_word_list.append(f"{key_word}_{string_word}")
                break

    return list(set(result_word_list))


def filter_dictionary_list(ori_list: list) -> list:
    """
    Filter out words present in the dictionary from a list.
    Args:
        ori_list (list): List of words to clean.
    Returns:
        list: List of words not in the dictionary.
    """
    return [word for word in ori_list if word not in DICTIONARY_WORDS_LIST]


def filter_dictionary_string(ori_string: str) -> str:
    """
    Filter out dictionary and blacklist words from a string.
    Args:
        ori_string (str): Original input string.
    Returns:
        str: Cleaned string.
    """
    clean_list = [
        word for word in ori_string.split(" ")
        if word not in BLACKLIST and not word.isdigit() and (1 < len(word) <= 25)
    ]
    return " ".join(clean_list)


def html_filter(html_str: str) -> str:
    """
    Clean and filter an HTML string to extract meaningful text.
    Args:
        html_str (str): The input HTML string.
    Returns:
        str: The cleaned text.
    """
    html_list = html_str.split("\n")
    html_clean_list = []
    id_ = 0

    for line in html_list:
        if line.startswith("<"):
            break
        id_ += 1
        if any(line.startswith(filter_word) for filter_word in HTTP_FILTER_LIST):
            continue
        html_clean_list.append(line.split(":")[-1])
    
    html_clean_list += html_list[id_:]
    html_str = "\n".join(html_clean_list)

    soup = BeautifulSoup(html_str, 'html.parser')

    # Remove unwanted HTML tags
    for tag in ['link', 'script', 'style']:
        for element in soup.find_all(tag):
            element.decompose()

    # Remove closing tags listed in the configuration
    for tag in HTML_TAGS_TO_REMOVE:
        for found_tag in soup.find_all(lambda t: str(t) == tag):
            found_tag.decompose()

    # Remove remaining HTML tags
    return re.sub(r'<[^>]+>', ' ', str(soup))


if __name__ == "__main__":
    sample_html = """
        ｴ\u0000\u0000h\u000f\u0000\u0000\u0000\u0007\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u00003J0677DPAM9BDBC
        <script>alert('Remove this!');</script>
        <style>body { background-color: red; }</style>
        """
    print(html_filter(sample_html))
