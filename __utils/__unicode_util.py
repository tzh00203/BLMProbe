"""  unicode 编码种类
Lu - 大写字母
Ll - 小写字母
Lt - 字母标题
Lm - 字母修饰符
Lo - 其他字母
Mn - 非间距调节标记
Mc - 间距调节标记
Me - 装饰修饰符
Nd - 十进制数字
Nl - 字母数字字符
No - 其他数字字符
Pc - 连字连接器
Pd - 破折号
Ps - 左括号
Pe - 右括号
Pi - 初始引号
Pf - 最终引号
Po - 其他标点符号
Sm - 数学符号
Sc - 货币符号
Sk - 连字符号
So - 其他符号
Zs - 空格分隔符
Zl - 行分隔符
Zp - 段落分隔符
Cc - 控制字符
Cf - 格式字符
Cs - 受限制的字符
"""
"""
Unicode Processing and Proportion Calculation Utilities:
1. Calculates the proportion of specific Unicode categories in a string.
2. Filters unwanted Unicode characters based on their category.
3. Handles hexadecimal escape sequences in strings.
"""

import unicodedata
import re


def unicode_calc_proportion(input_string: str) -> float:
    """
    Calculate the proportion of characters in a string that belong to specific Unicode categories.
    Excludes Chinese characters and standard whitespace.
    Args:
        input_string (str): The input string to analyze.
    Returns:
        float: The proportion of specific Unicode category characters in the string.
    """
    unwanted_categories = {"Cc", "Cf", "Cs", "Sc", "Lo", "So"}
    unwanted_count = 0

    for char in input_string:
        unicode_type = unicodedata.category(char)
        # Count if character is in unwanted categories and not standard whitespace
        if not (u'\u4e00' <= char <= u'\u9fff') and unicode_type in unwanted_categories:
            if char not in {'\n', '\t', '\r'}:
                unwanted_count += 1

    return unwanted_count / len(input_string) if input_string else 0.0


def hex_calc_proportion(input_string: str) -> float:
    """
    Calculate the proportion of hexadecimal escape sequences (e.g., \xHH) in a string.
    Args:
        input_string (str): The input string to analyze.
    Returns:
        float: The proportion of hexadecimal sequences in the string.
    """
    # Remove hexadecimal escape sequences
    string_without_hex = re.sub(r'\\x[0-9a-fA-F]{2}', '', input_string)
    # Calculate the proportion of hex sequences
    return 1 - (len(string_without_hex) / len(input_string)) if input_string else 0.0


def unicode_filter(input_string: str) -> str:
    """
    Filter out characters based on their Unicode category.
    Replaces unwanted characters with a space.
    Args:
        input_string (str): The input string to filter.
    Returns:
        str: The filtered string.
    """
    unwanted_categories = {"Cc", "Cf", "Cs", "Sc", "Lo", "So", "No", "Pi", "Pf", "Sk", "Ps", "Pe", "Po", "Sm"}
    filtered_string = ""

    for char in input_string:
        unicode_type = unicodedata.category(char)
        if unicode_type in unwanted_categories and char != ".":
            char = " "
        filtered_string += char

    # Replace commas with spaces and normalize whitespace
    filtered_string = filtered_string.replace(",", " ")
    return re.sub(r'\s+', ' ', filtered_string).strip()


def punc_filter(input_string: str) -> str:
    """
    Filter punctuation characters based on Unicode categories.
    Currently not implemented for specific punctuation filtering.
    Args:
        input_string (str): The input string to filter.
    Returns:
        str: The filtered string.
    """
    filtered_string = ""

    for char in input_string:
        unicode_type = unicodedata.category(char)
        # Add logic to filter specific punctuation if needed
        filtered_string += char

    # Replace commas with spaces and normalize whitespace
    filtered_string = filtered_string.replace(",", " ")
    return re.sub(r'\s+', ' ', filtered_string).strip()


def untural2train(unnatural_string: str) -> str:
    """
    Placeholder function for converting unnatural strings to normalized format.
    Args:
        unnatural_string (str): The input string to process.
    Returns:
        str: The processed string (currently not implemented).
    """
    # Future implementation for unnatural string normalization
    return unnatural_string


# ========================= Main Test =========================

if __name__ == "__main__":
    sample_string = "\r\n\r\nHello! This is a test string with \\x02 hexadecimal values and \u3000 Unicode characters."
    
    print("Hexadecimal Proportion:", hex_calc_proportion(sample_string))
    print("Unicode Proportion:", unicode_calc_proportion(sample_string))
    print("Filtered Unicode String:", unicode_filter(sample_string))
    print("Filtered Punctuation String:", punc_filter(sample_string))
