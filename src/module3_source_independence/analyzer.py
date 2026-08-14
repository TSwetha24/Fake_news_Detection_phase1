import numpy as np
import config
from src.module3_source_independence.sentence_bert_encoder import SentenceBERTEncoder
from src.module3_source_independence.clustering import ArticleClusterer

class SourceIndependenceAnalyzer:
    """
    MODULE 3: Source Independence Analysis Module
    Algorithms / Techniques: Sentence-BERT, Cosine Similarity, Clustering
    
    Identifies duplicate or related articles to estimate the number of independent supporting sources.
    Calculates Pairwise Cosine Similarity:
        S(i,j) = (e_i . e_j) / (||e_i|| ||e_j||)
    Articles with S(i,j) >= Cosine Threshold (0.75) are grouped into the same syndicated cluster.
    """
    def __init__(self, threshold=config.COSINE_SIMILARITY_THRESHOLD):
        print("[Module 3] Initializing Source Independence Analyzer (Sentence-BERT, Cosine Similarity, Agglomerative Clustering)...")
        self.encoder = SentenceBERTEncoder()
        self.clusterer = ArticleClusterer(threshold=threshold)
        self.threshold = threshold

    def analyze(self, evidence_items: list):
        """
        Analyzes a list of retrieved evidence articles for source independence.
        """
        if not evidence_items:
            return {
                "total_articles_analyzed": 0,
                "independent_sources_count": 0,
                "source_independence_score": 0.0,
                "duplication_rate_percent": 0.0,
                "cosine_threshold": self.threshold,
                "nodes": [],
                "edges": [],
                "pairwise_similarity_matrix": [],
                "clusters": []
            }

        # 1. Encode articles using Sentence-BERT embeddings
        embeddings = self.encoder.encode_articles(evidence_items)

        # 2. Perform Cosine Similarity matrix & Agglomerative Clustering
        labels, clusters_summary, sim_matrix = self.clusterer.cluster_articles(embeddings, evidence_items)

        total_articles = len(evidence_items)
        n_independent_clusters = len(clusters_summary)
        
        # Calculate Source Independence Score: Ratio of unique clusters K to total articles N
        independence_score = round(n_independent_clusters / float(total_articles), 4)
        duplication_rate = round((1.0 - independence_score) * 100, 2)

        # Build Graph Nodes & Edges for UI Cluster Visualizer
        nodes = []
        for idx, art in enumerate(evidence_items):
            cluster_id = int(labels[idx]) if idx < len(labels) else 0
            nodes.append({
                "id": idx,
                "label": art.get("domain", "source"),
                "title": art.get("title", ""),
                "domain": art.get("domain", ""),
                "source": art.get("source", ""),
                "cluster_id": cluster_id,
                "url": art.get("url", "#"),
                "publish_date": art.get("publish_date", "2026-08-13")
            })

        edges = []
        n = len(evidence_items)
        for i in range(n):
            for j in range(i + 1, n):
                sim_val = float(sim_matrix[i, j])
                if sim_val >= self.threshold:
                    edges.append({
                        "source": i,
                        "target": j,
                        "similarity": round(sim_val, 4),
                        "cluster_id": int(labels[i])
                    })

        # Format cluster summary objects
        formatted_clusters = []
        for cluster_id, arts in clusters_summary.items():
            primary_art = arts[0]
            domains = list(set([a.get('domain', 'Unknown') for a in arts]))
            
            formatted_clusters.append({
                "cluster_id": cluster_id,
                "primary_headline": primary_art.get("title", ""),
                "article_count": len(arts),
                "domains_involved": domains,
                "is_syndicated": True if len(arts) > 1 else False,
                "articles": [
                    {
                        "title": a.get("title", ""),
                        "source": a.get("source", ""),
                        "domain": a.get("domain", ""),
                        "url": a.get("url", "")
                    }
                    for a in arts
                ]
            })

        sim_matrix_list = np.round(sim_matrix, 3).tolist() if len(sim_matrix) > 0 else []

        return {
            "total_articles_analyzed": total_articles,
            "independent_sources_count": n_independent_clusters,
            "source_independence_score": independence_score,
            "duplication_rate_percent": duplication_rate,
            "cosine_threshold": self.threshold,
            "nodes": nodes,
            "edges": edges,
            "pairwise_similarity_matrix": sim_matrix_list,
            "clusters": formatted_clusters
        }
