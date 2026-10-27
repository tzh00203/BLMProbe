"""
Similarity Measurement Utilities:
1. Multiple similarity algorithms including:
   - Edit distance, Hamming distance, Levenshtein ratio, Jaro, Jaro-Winkler, LCS, Dice, WordNet, Cosine similarity.
2. Supports both semantic and syntactic similarity.

Dependencies:
   - `Levenshtein`: For string distance calculations.
   - `jieba`: For Chinese word segmentation.
   - `nltk`: For WordNet-based semantic similarity.
"""

import Levenshtein
from nltk.corpus import wordnet as wn
import jieba
import math

# Default similarity threshold
SIMILARITY_THRESHOLD = 0.9


def similarity(word1: str, word2: str, method: str = "jaro_winkler") -> list:
    """
    Compute similarity between two words using the specified method.
    Args:
        word1 (str): First word.
        word2 (str): Second word.
        method (str): Similarity algorithm to use.
                      Options: ['edit', 'hamming', 'leven', 'jaro', 'jaro_winkler', 'lcs', 'dice', 'wordnet', 'cos']
    Returns:
        list: [Description string, Similarity value]
    """
    method_map = {
        'edit': edit_sim,
        'hamming': hamming_sim,
        'leven': leven_sim,
        'jaro': jaro_sim,
        'jaro_winkler': jaro_winkler_sim,
        'lcs': lcs_sim,
        'dice': dice_sim,
        'wordnet': wordnet_sim,
        'cos': cos_similarity
    }

    if method not in method_map:
        raise ValueError(f"Invalid method: {method}. Available methods: {list(method_map.keys())}")
    
    sim_result = method_map[method](word1, word2)
    return [
        f"The similarity ({method}) between '{word1}' and '{word2}': {sim_result:.2f}",
        sim_result
    ]


# ==================== Similarity Algorithms ====================

def edit_sim(word1: str, word2: str) -> float:
    """Calculate similarity using Edit Distance."""
    max_len = max(len(word1), len(word2))
    return 1 - Levenshtein.distance(word1, word2) / max_len


def hamming_sim(word1: str, word2: str) -> float:
    """Calculate similarity using Hamming Distance."""
    max_len = max(len(word1), len(word2))
    if len(word1) > len(word2):
        word1 = word1[:len(word2)]
    else:
        word2 = word2[:len(word1)]
    return 1 - Levenshtein.hamming(word1, word2) / max_len


def leven_sim(word1: str, word2: str) -> float:
    """Calculate similarity using Levenshtein Ratio."""
    return Levenshtein.ratio(word1, word2)


def jaro_sim(word1: str, word2: str) -> float:
    """Calculate similarity using Jaro Distance."""
    return Levenshtein.jaro(word1, word2)


def jaro_winkler_sim(word1: str, word2: str) -> float:
    """Calculate similarity using Jaro-Winkler Distance."""
    return Levenshtein.jaro_winkler(word1, word2)


def lcs_sim(word1: str, word2: str) -> float:
    """Calculate similarity using Longest Common Subsequence (LCS)."""
    max_len = max(len(word1), len(word2))
    dp = [[0] * (len(word2) + 1) for _ in range(len(word1) + 1)]
    for i in range(len(word1) - 1, -1, -1):
        for j in range(len(word2) - 1, -1, -1):
            if word1[i] == word2[j]:
                dp[i][j] = dp[i + 1][j + 1] + 1
            else:
                dp[i][j] = max(dp[i + 1][j], dp[i][j + 1])
    return dp[0][0] / max_len


def dice_sim(word1: str, word2: str) -> float:
    """Calculate similarity using Dice Coefficient."""
    bigrams1 = set(word1)
    bigrams2 = set(word2)
    overlap = len(bigrams1 & bigrams2)
    return 2 * overlap / (len(bigrams1) + len(bigrams2))


def wordnet_sim(word1: str, word2: str) -> float:
    """
    Calculate semantic similarity using WordNet.
    Args:
        word1 (str): First word or phrase.
        word2 (str): Second word or phrase.
    Returns:
        float: Semantic similarity score.
    """
    max_similarity = 0.0
    for synset1 in wn.synsets(word1):
        for synset2 in wn.synsets(word2):
            sim = synset1.path_similarity(synset2)
            if sim:
                max_similarity = max(max_similarity, sim)
    return max_similarity


def cos_similarity(s1: str, s2: str) -> float:
    """
    Calculate similarity using Cosine Similarity.
    Args:
        s1 (str): First string.
        s2 (str): Second string.
    Returns:
        float: Cosine similarity score.
    """
    s1_cut = [i for i in jieba.cut(s1) if i]
    s2_cut = [i for i in jieba.cut(s2) if i]
    word_set = set(s1_cut).union(set(s2_cut))

    word_dict = {word: idx for idx, word in enumerate(word_set)}
    s1_vec = [0] * len(word_dict)
    s2_vec = [0] * len(word_dict)

    for word in s1_cut:
        s1_vec[word_dict[word]] += 1
    for word in s2_cut:
        s2_vec[word_dict[word]] += 1

    dot_product = sum(a * b for a, b in zip(s1_vec, s2_vec))
    magnitude1 = math.sqrt(sum(a ** 2 for a in s1_vec))
    magnitude2 = math.sqrt(sum(b ** 2 for b in s2_vec))

    return dot_product / (magnitude1 * magnitude2) if magnitude1 and magnitude2 else 0.0


# ========================= Main Test =========================

if __name__ == "__main__":
    result = similarity("asp", "ap", method="jaro_winkler")
    print(result[0])  # Human-readable description
    print(f"Similarity Score: {result[1]:.2f}")  # Numerical score
