"""
Concurrent Bing Search Crawler:
Performs concurrent searches on Bing using high-frequency keywords identified by TF-IDF.
"""

import sys
import os
import queue
import time
from multiprocessing import Process
from pathlib import Path

# Add parent directory to the system path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from __crawler_bing_util import bing_api_search
from __crawler_google_util import google_api_search
from __logs.__log import log_init
from __utils.__path_util import global_path
from __crawler_config import *

# Path to the TF-IDF file
TFIDF_PATH = global_path.__crawler_tfidf_path__


def load_tfidf():
    """
    Load TF-IDF keywords and their indices from the specified file.
    Returns:
        tuple: Two lists - a list of search indices and a list of search queries.
    """
    with open(TFIDF_PATH, "r", encoding="utf-8") as f:
        tfidf_dict = eval(f.read())

    tfidf_search_words_dict = {}
    for index, words in tfidf_dict.items():
        words_str = str(words)
        if words_str not in tfidf_search_words_dict:
            tfidf_search_words_dict[words_str] = [index]
        else:
            tfidf_search_words_dict[words_str].append(index)

    return list(tfidf_search_words_dict.values()), list(tfidf_search_words_dict.keys())


class Crawler:
    def __init__(self, mode='Bing'):
        self.search_cnt = 0
        self.search_limit = 100
        self.query_dict = {}
        self.mode = mode
    def crawler_concurrent(self, search_query, search_index, start: int, end: int, search_func=bing_api_search, mode='Bing'):
        """
        Perform Bing search on a subset of queries concurrently.
        Args:
            search_query (list): List of search queries.
            search_index (list): List of corresponding indices for each query.
            start (int): Start index for the subset of queries.
            end (int): End index for the subset of queries.
        """
        # Subset of data for this process
        queries_subset = search_query[start:end + 1]
        indices_subset = search_index[start:end + 1]
        num_queries = len(queries_subset)

        # Initialize logger for this process
        logger_path = f"{global_path.__crawler_search_result_path__}search_log/search_uri_{start}_{end}.log"
        logger = log_init(log_filename=logger_path)

        # Initialize a queue for processing
        query_queue = queue.Queue(num_queries)
        for query_str, indices in zip(queries_subset, indices_subset):
            line_index = "_".join(indices)
            query = " ".join(eval(query_str))  # Convert string representation back to a list
            query_queue.put([query, line_index])

        while not query_queue.empty():
            query, line_index = query_queue.get()
            logger.info(f"===================== {query_queue.qsize()} " + mode + " queries remaining =====================")
            key = (query, line_index)
            if self.query_dict.get(key, 0) >= QUEUE_RETRY_COUNT:
                continue

            search_results = search_func(query)
            uri_list = search_results[0] if search_results else []

            if uri_list:
                for uri in uri_list:
                    logger.info(f"Sanitization Line: {line_index} | {mode} URI: {uri}")
            else:
                query_queue.put([query, line_index])

            self.query_dict[key] = self.query_dict.get(key, 0) + 1
            time.sleep(TIME_SLEEP)


    def bing_crawler(self):
        # Load TF-IDF data
        search_indices, search_queries = load_tfidf()
        total_queries = len(search_queries)

        print(f"Total Bing searches to process: {total_queries}")

        # Define process parameters
        process_count = PROCESS_COUNT
        queries_per_process = total_queries // process_count

        # Launch concurrent processes
        processes = []
        for i in range(process_count):
            start_idx = i * queries_per_process
            end_idx = (i + 1) * queries_per_process - 1 if i < process_count - 1 else total_queries - 1

            process = Process(target=self.crawler_concurrent, args=(search_queries, search_indices, start_idx, end_idx))
            processes.append(process)
            process.start()

        # Wait for all processes to complete
        for process in processes:
            process.join()

        print("All Bing searches completed.")

    def google_crawler(self):
        # Load TF-IDF data
        search_indices, search_queries = load_tfidf()
        total_queries = len(search_queries)

        print(f"Total Google searches to process: {total_queries}")
        # Define process parameters
        process_count = PROCESS_COUNT
        queries_per_process = total_queries // process_count

        # Launch concurrent processes
        processes = []
        for i in range(process_count):
            start_idx = i * queries_per_process
            end_idx = start_idx + 68
            # end_idx = (i + 1) * queries_per_process - 1 if i < process_count - 1 else total_queries - 1 - 5058

            process = Process(
                target=self.crawler_concurrent, 
                args=(search_queries, search_indices, start_idx, end_idx, google_api_search, 'Google')
            )
            processes.append(process)
            process.start()

        # Wait for all processes to complete
        for process in processes:
            process.join()

        print("All Google searches completed.")

    def run_crawler(self):
        dirname = dirname = Path(f"{global_path.__crawler_search_result_path__}search_log/")
        if not dirname.exists():
            dirname.mkdir(parents=True, exist_ok=True)
        for filename in os.listdir(dirname):
            os.remove(dirname + filename)
        if self.mode=='Bing': self.bing_crawler()
        elif self.mode=='Google': self.google_crawler()


if __name__ == "__main__":
    crawler = Crawler()
    # bing_crawler()
    crawler.google_crawler()
