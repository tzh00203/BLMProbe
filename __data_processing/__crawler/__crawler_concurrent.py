"""
Concurrent Bing Search Crawler:
Performs concurrent searches on Bing using high-frequency keywords identified by TF-IDF.
"""

import os
import sys
import queue
import time
from multiprocessing import Process

# Add parent directory to the system path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from __crawler_bing_util import bing_api_search
from __logs.__log import log_init
from __utils.__path_util import global_path


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


def crawler_concurrent(search_query, search_index, start: int, end: int):
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
    logger = log_init(logFilename=logger_path)

    # Initialize a queue for processing
    query_queue = queue.Queue(num_queries)
    for query_str, indices in zip(queries_subset, indices_subset):
        line_index = "_".join(indices)
        query = " ".join(eval(query_str))  # Convert string representation back to a list
        query_queue.put([query, line_index])

    while not query_queue.empty():
        query, line_index = query_queue.get()
        logger.info(f"===================== {query_queue.qsize()} queries remaining =====================")
        search_results = bing_api_search(query)

        # Process the search results
        uri_list = search_results[0] if search_results else []
        if uri_list:
            for uri in uri_list:
                logger.info(f"Sanitization Line: {line_index} | Bing URI: {uri}")
        else:
            # Re-add query to the queue if no results are found
            query_queue.put([query, line_index])


if __name__ == "__main__":
    # Load TF-IDF data
    search_indices, search_queries = load_tfidf()
    total_queries = len(search_queries)

    print(f"Total Bing searches to process: {total_queries}")

    # Define process parameters
    process_count = 5
    queries_per_process = total_queries // process_count

    # Launch concurrent processes
    processes = []
    for i in range(process_count):
        start_idx = i * queries_per_process
        end_idx = (i + 1) * queries_per_process - 1 if i < process_count - 1 else total_queries - 1

        process = Process(target=crawler_concurrent, args=(search_queries, search_indices, start_idx, end_idx))
        processes.append(process)
        process.start()

    # Wait for all processes to complete
    for process in processes:
        process.join()

    print("All Bing searches completed.")
