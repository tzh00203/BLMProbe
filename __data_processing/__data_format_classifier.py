# -*- coding:utf-8 -*-
"""
Response Data Analysis and Clustering:
1. Load and process response data.
2. Embed response data into feature vectors.
3. Perform dichotomy using K-Means clustering.
4. Save results and visualize clustering.

Dependencies:
- `numpy` for numerical operations.
- `matplotlib` for visualization.
"""

import json
import re
import numpy as np
from matplotlib import pyplot as plt
from __utils.__path_util import global_path
from __utils.__save_file_util import save_dict_to_json
from __utils.__unicode_util import unicode_calc_proportion

# Global paths
ROOT_PATH = global_path.__raw_data_path__
data_path = global_path.__data_for_classify_path__
output_path = global_path.__text_path__

def load_all_response():
    """
    Load all IoT asset responses.
    """
    all_response_dict = json.load(open(data_path, "r", encoding="utf-8"))
    combined_responses = {"all_response": []}

    for ip, ip_data in all_response_dict.items():
        print(f"Processing IP: {ip}")
        combined_responses["all_response"].extend(ip_data["response_data"])

    return combined_responses

def data_embedding():
    """
    Embed response data into a 4-dimensional feature vector:
    [Space count, Line count, Unicode proportion, String length]
    Returns:
        list: List of embedded data points with original response.
    """
    embedding_dict = {
        "natural language": [],
        "unnatural language": []
    }
    embedding_data_list = []

    all_response = load_all_response
    for cnt, line in enumerate(all_response["all_response"], start=1):
        if not line:
            continue
        print(f"Embedding response #{cnt}")

        # Compute feature values
        space_count = line.count(" ")
        line_count = line.count("\r\n")
        uu_proportion = unicode_calc_proportion(line)
        str_len = len(line)

        # Label based on threshold
        is_natural = uu_proportion <= 0.2

        # Append embedding and classify
        embedding_data_list.append([space_count, line_count, uu_proportion, str_len, line])
        if is_natural:
            embedding_dict["natural language"].append(line)
        else:
            embedding_dict["unnatural language"].append(line)

    save_dict_to_json(f"{ROOT_PATH}raw_data/all_response_dichotomy_v1.json", embedding_dict)
    return embedding_data_list


class KMeans:
    """
    Custom K-Means clustering implementation.
    Attributes:
        response_data: List of raw responses.
        k: Number of clusters.
        tolerance: Threshold for convergence.
        max_iter: Maximum number of iterations.
    """
    def __init__(self, response_data, k=2, tolerance=0.0001, max_iter=300):
        self.response_data = response_data
        self.k = k
        self.tolerance = tolerance
        self.max_iter = max_iter
        self.centers = {}
        self.clusters = {}
        self.result_labels = []

    def fit(self, data):
        """
        Fit the K-Means model to the data.
        Args:
            data (ndarray): Data points for clustering.
        """
        # Initialize cluster centers
        self.centers = {i: data[i] for i in range(self.k)}

        for iteration in range(self.max_iter):
            self.clusters = {i: [] for i in range(self.k)}
            self.result_labels = []

            # Assign data points to the nearest center
            for feature in data:
                distances = [np.linalg.norm(feature - self.centers[center]) for center in self.centers]
                classification = distances.index(min(distances))
                self.clusters[classification].append(feature)
                self.result_labels.append(classification)

            # Update cluster centers
            previous_centers = dict(self.centers)
            for cluster_id in self.clusters:
                self.centers[cluster_id] = np.mean(self.clusters[cluster_id], axis=0)

            # Check for convergence
            optimized = True
            for cluster_id in self.centers:
                if np.sum((self.centers[cluster_id] - previous_centers[cluster_id]) / previous_centers[cluster_id]) > self.tolerance:
                    optimized = False

            if optimized:
                print(f"Converged after {iteration + 1} iterations.")
                break

    def predict(self, data_point):
        """
        Predict the cluster label for a new data point.
        Args:
            data_point (ndarray): Input data point.
        Returns:
            int: Predicted cluster label.
        """
        distances = [np.linalg.norm(data_point - self.centers[center]) for center in self.centers]
        return distances.index(min(distances))

    def save_result(self):
        """
        Save clustering results as JSON files.
        """
        embedding_dict = {
            "natural language": [],
            "unnatural language": []
        }
        text_dict = {"text_data": []}
        for idx, label in enumerate(self.result_labels):
            if label == 1:
                embedding_dict["natural language"].append(self.response_data[idx])
                text_dict["text_data"].append(self.response_data[idx])
            else:
                embedding_dict["unnatural language"].append(self.response_data[idx])

        save_dict_to_json(output_path, text_dict)


def calc():
    """
    Main function to perform K-Means clustering and visualize results.
    """
    embedded_data = data_embedding()
    feature_data = []
    responses = []

    for entry in embedded_data:
        feature_data.append([entry[0] + 1, entry[1] + 1, entry[2], entry[3]])
        responses.append(entry[-1])

    feature_data = np.array(feature_data)
    k_means = KMeans(response_data=responses, k=2)
    k_means.fit(feature_data)
    k_means.save_result()

    # # Visualization
    # for cluster_id in k_means.clusters:
    #     cluster_data = np.array(k_means.clusters[cluster_id])
    #     plt.scatter(cluster_data[:, 0], cluster_data[:, 1], label=f"Cluster {cluster_id}")

    # for center_id, center_coords in k_means.centers.items():
    #     plt.scatter(center_coords[0], center_coords[1], marker='*', s=150, color='black', label=f"Center {center_id}")

    # # plt.legend()
    # # plt.title("K-Means Clustering of Response Data")
    # # plt.show()


if __name__ == "__main__":
    calc()
