import numpy as np
import torch
import torch.nn.functional as F
from sklearn.cluster import KMeans
from gensim.downloader import load

# Load GloVe embeddings (100-dimensional vectors)
word_vectors = load("glove-wiki-gigaword-100")

def cluster_words(word_list, k):
    """
    Clusters words using GloVe embeddings and K-Means clustering.

    Parameters:
    - word_list: List of words to cluster.
    - k: Number of clusters.

    Prints the clusters with their representative words.
    """
    # Filter words that exist in the GloVe vocabulary
    filtered_words = [word for word in word_list if word in word_vectors]
    if len(filtered_words) < k:
        print(f"Not enough valid words for {k} clusters. Using {len(filtered_words)} instead.")
        k = min(len(filtered_words), k)

    # Get word embeddings
    word_embeddings = np.array([word_vectors[word] for word in filtered_words])

    # Apply K-Means clustering
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(word_embeddings)
    labels = kmeans.labels_

    # Group words by cluster and find the most representative word
    clusters = {}
    for i, word in enumerate(filtered_words):
        cluster_id = labels[i]
        if cluster_id not in clusters:
            clusters[cluster_id] = []
        clusters[cluster_id].append(word)

    # Find the most representative word in each cluster (closest to centroid)
    cluster_representatives = {}
    for cluster_id, words in clusters.items():
        cluster_vectors = np.array([word_vectors[word] for word in words])
        centroid = kmeans.cluster_centers_[cluster_id]

        # Compute distances to centroid
        distances = np.linalg.norm(cluster_vectors - centroid, axis=1)

        # Select the word closest to the centroid
        best_word = words[np.argmin(distances)]
        cluster_representatives[cluster_id] = best_word

    # Print results
    for cluster_id, words in clusters.items():
        print(f"\nCluster {cluster_id + 1}: Representative Word -> {cluster_representatives[cluster_id]}")
        print("Words in this cluster:", words)

word_list = [
    "king", "queen", "prince", "princess", "throne", "royalty",
    "cow", "sheep", "dog", "cat", "wolf", "lion", "tiger", "cheetah",
    "apple", "banana", "grape", "fruit", "mango", "peach",
    "car", "bus", "truck", "train", "bike", "vehicle",
    "happy", "joy", "cheerful", "smiling", "laughter", "delighted"
]

k = 5  # Set the number of clusters
cluster_words(word_list, k)
