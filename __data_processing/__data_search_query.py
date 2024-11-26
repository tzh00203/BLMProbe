"""
TF-IDF Based Search Query Setup:
1. Extract sanitized strings from the dataset to build a text corpus.
2. Compute TF-IDF scores for each document in the corpus.
3. Extract top keywords and save them for search query generation.
"""

import json
from __utils.__save_file_util import save_dict_to_json
from __data_TFIDF_util import tfidf_calc
from __utils.__path_util import global_path
from __data_sanitization import load_data


# Global Paths
RAW_DATA_PATH = global_path.__sani_path__
TFIDF_PATH = global_path.__crawler_tfidf_path__
KEYWORDS_NUM = 7  # Number of top keywords to extract


class TFIDFProcessor:
    """
    Process sanitized data to generate a corpus, compute TF-IDF, and prepare search queries for crawlers.
    """

    @staticmethod
    def corpus_init() -> tuple:
        """
        Initialize corpus from sanitized data.
        :return: Tuple (corpus, corpus_id)
        """
        try:
            # with open(RAW_DATA_PATH, "r", encoding="utf-8") as raw_file:
            #     data_sanitization_dict = json.load(raw_file)
            data_sanitization_dict = load_data()

            corpus, corpus_id, corpus_dict = [], [], {}
            for idx, line in enumerate(data_sanitization_dict["sanitization_data"]):
                if line:
                    corpus.append(line)
                    corpus_id.append(idx + 3)  # Offset ID by 3 as per the existing logic
                    corpus_dict[idx + 3] = line

            return corpus, corpus_id

        except Exception as e:
            print(f"Error initializing corpus: {e}")
            return [], []

    @staticmethod
    def compute_tfidf(corpus: list, corpus_id: list) -> dict:
        """
        Compute TF-IDF for the given corpus.
        :param corpus: List of strings representing the text corpus.
        :param corpus_id: List of document IDs corresponding to the corpus.
        :return: Dictionary of top keywords for each document ID.
        """
        try:
            return tfidf_calc(corpus, corpus_id)
        except Exception as e:
            print(f"Error computing TF-IDF: {e}")
            return {}

    @staticmethod
    def save_search_queries(words_dict: dict):
        """
        Save the search query setup based on TF-IDF keywords.
        :param words_dict: Dictionary of keywords per document ID.
        """
        try:
            save_dict_to_json(TFIDF_PATH, words_dict)
            print("Search queries saved successfully.")
        except Exception as e:
            print(f"Error saving search queries: {e}")


if __name__ == "__main__":
    # Step 1: Initialize Corpus
    tfidf_processor = TFIDFProcessor()
    corpus, corpus_id = tfidf_processor.corpus_init()

    # Step 2: Compute TF-IDF
    if corpus and corpus_id:
        tfidf_keywords = tfidf_processor.compute_tfidf(corpus, corpus_id)

        # Step 3: Save Search Queries
        if tfidf_keywords:
            tfidf_processor.save_search_queries(tfidf_keywords)
