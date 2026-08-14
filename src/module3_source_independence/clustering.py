import numpy as np
from sklearn.cluster import AgglomerativeClustering, DBSCAN
from sklearn.metrics.pairwise import cosine_similarity
import config

class ArticleClusterer:
    """
    Article Clustering Engine.
    Groups duplicate, syndicated, or copy-pasted articles together based on cosine similarity thresholds.
    Each cluster represents a single independent origin story/source.
    """
    def __init__(self, threshold=config.COSINE_SIMILARITY_THRESHOLD):
        self.threshold = threshold

    def cluster_articles(self, embeddings, articles):
        """
        Input:
            embeddings: (N, D) numpy array of vector embeddings
            articles: list of article dicts of length N
        Returns:
            - cluster_labels: list of cluster IDs for each article
            - clusters_summary: dict summarizing each cluster and its member articles
        """
        n_samples = len(articles)
        if n_samples == 0:
            return [], {}
        if n_samples == 1:
            return [0], {0: [articles[0]]}

        # Calculate Pairwise Cosine Distance matrix (Distance = 1 - Cosine Similarity)
        sim_matrix = cosine_similarity(embeddings)
        dist_matrix = np.clip(1.0 - sim_matrix, 0.0, 2.0)
        
        distance_threshold = 1.0 - self.threshold

        # Agglomerative Hierarchical Clustering with distance threshold
        clustering = AgglomerativeClustering(
            n_clusters=None,
            metric='precomputed',
            linkage='complete',
            distance_threshold=distance_threshold
        )
        
        labels = clustering.fit_predict(dist_matrix)
        
        clusters_summary = {}
        for idx, cluster_id in enumerate(labels):
            cluster_id = int(cluster_id)
            if cluster_id not in clusters_summary:
                clusters_summary[cluster_id] = []
            
            art_info = dict(articles[idx])
            art_info['cluster_id'] = cluster_id
            clusters_summary[cluster_id].append(art_info)

        return labels.tolist(), clusters_summary, sim_matrix
