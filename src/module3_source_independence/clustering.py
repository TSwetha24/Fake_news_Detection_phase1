import re
import numpy as np
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_similarity
import config

KNOWN_DOMAINS_MAP = {
    "the hindu": "thehindu.com",
    "thehindu": "thehindu.com",
    "times of india": "timesofindia.indiatimes.com",
    "the times of india": "timesofindia.indiatimes.com",
    "timesofindia": "timesofindia.indiatimes.com",
    "ndtv": "ndtv.com",
    "news18": "news18.com",
    "the indian express": "indianexpress.com",
    "indian express": "indianexpress.com",
    "indianexpress": "indianexpress.com",
    "hindustan times": "hindustantimes.com",
    "hindustantimes": "hindustantimes.com",
    "india today": "indiatoday.in",
    "indiatoday": "indiatoday.in",
    "deccan herald": "deccanherald.com",
    "deccanherald": "deccanherald.com",
    "the print": "theprint.in",
    "theprint": "theprint.in",
    "the quint": "thequint.com",
    "thequint": "thequint.com",
    "bbc": "bbc.com",
    "bbc news": "bbc.com",
    "reuters": "reuters.com",
    "ani": "aninews.in",
    "ani news": "aninews.in",
    "pti": "ptinews.com",
    "press trust of india": "ptinews.com",
    "wikipedia": "en.wikipedia.org",
    "duckduckgo": "duckduckgo.com",
    "gdelt": "gdeltproject.org",
    "newsapi": "newsapi.org",
    "moneycontrol": "moneycontrol.com",
    "livemint": "livemint.com",
    "economic times": "economictimes.indiatimes.com",
    "dt next": "dtnext.in",
    "cinema express": "cinemaexpress.com",
}


def extract_base_publisher(domain: str, source: str = "", title: str = "") -> str:
    """
    Normalizes domain and publisher source name into a canonical publisher identifier.
    Groups subdomains and variations (e.g. 'm.thehindu.com', 'The Hindu', 'thehindu.com')
    into a single canonical publisher identity.
    """
    domain_clean = domain.lower().replace("http://", "").replace("https://", "").split("/")[0]
    if domain_clean.startswith("www."):
        domain_clean = domain_clean[4:]

    # Check known domain mappings from source name
    source_lower = source.lower()
    for key, canonical in KNOWN_DOMAINS_MAP.items():
        if key in source_lower or key in domain_clean:
            return canonical

    # Extract publisher from title suffixes like "... - The Hindu" or "... | NDTV"
    for sep in [" - ", " | ", " — "]:
        if sep in title:
            tail = title.split(sep)[-1].strip().lower()
            for key, canonical in KNOWN_DOMAINS_MAP.items():
                if key in tail:
                    return canonical

    return domain_clean if domain_clean else "unknown.com"


class ArticleClusterer:
    """
    Article Clustering Engine for Source Independence.
    Groups duplicate, syndicated, or copy-pasted articles AND articles from the same
    source/publisher together based on composite similarity.
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
            - cluster_labels: list of cluster IDs for each article (0-indexed)
            - clusters_summary: dict summarizing each cluster and its member articles
            - sim_matrix: composite (N, N) pairwise similarity matrix
        """
        n_samples = len(articles)
        if n_samples == 0:
            return [], {}, np.zeros((0, 0))
        if n_samples == 1:
            return [0], {0: [articles[0]]}, np.ones((1, 1))

        # 1. Base semantic cosine similarity from embeddings
        if embeddings is not None and len(embeddings) == n_samples and embeddings.ndim == 2:
            base_sim = cosine_similarity(embeddings)
        else:
            base_sim = np.zeros((n_samples, n_samples))

        # 2. Extract canonical publishers for each article
        publishers = [
            extract_base_publisher(
                a.get("domain", ""),
                a.get("source", ""),
                a.get("title", "")
            )
            for a in articles
        ]

        # 3. Compute Composite Pairwise Similarity Matrix S(i, j)
        sim_matrix = np.zeros((n_samples, n_samples))
        for i in range(n_samples):
            for j in range(n_samples):
                if i == j:
                    sim_matrix[i, j] = 1.0
                    continue

                # A. Source / Publisher Identity Match
                # Articles from the SAME news organization share an origin -> high similarity
                same_publisher = (publishers[i] == publishers[j] and publishers[i] not in ["google.com", "news.google.com", "unknown.com"])
                pub_score = 0.88 if same_publisher else 0.0

                # B. Textual Word Jaccard / N-Gram Overlap on titles
                t1 = re.sub(r'[^\w\s]', '', articles[i].get("title", "").lower()).split()
                t2 = re.sub(r'[^\w\s]', '', articles[j].get("title", "").lower()).split()
                s1, s2 = set(t1), set(t2)
                jaccard = len(s1 & s2) / max(1, len(s1 | s2))
                jaccard_score = 0.85 if jaccard >= 0.40 else (jaccard * 1.5 if jaccard >= 0.25 else 0.0)

                # C. Semantic Cosine Similarity
                sem_score = float(base_sim[i, j])

                # Composite score: maximum evidence of duplication/syndication
                composite_score = max(pub_score, sem_score, jaccard_score)
                sim_matrix[i, j] = round(min(composite_score, 1.0), 4)

        # 4. Graph Connected Components / Agglomerative Clustering
        # Cluster threshold: default 0.50 (articles with S(i, j) >= 0.50 merge into one cluster)
        adj_matrix = (sim_matrix >= self.threshold)
        visited = [False] * n_samples
        labels = [0] * n_samples
        clusters_summary = {}
        cluster_id = 0

        for i in range(n_samples):
            if not visited[i]:
                component_indices = []
                queue = [i]
                visited[i] = True

                while queue:
                    curr = queue.pop(0)
                    component_indices.append(curr)
                    labels[curr] = cluster_id

                    for neighbor in range(n_samples):
                        if not visited[neighbor] and adj_matrix[curr, neighbor]:
                            visited[neighbor] = True
                            queue.append(neighbor)

                # Store cluster summary
                cluster_arts = []
                for idx in component_indices:
                    art_info = dict(articles[idx])
                    art_info["cluster_id"] = cluster_id
                    art_info["canonical_publisher"] = publishers[idx]
                    cluster_arts.append(art_info)

                clusters_summary[cluster_id] = cluster_arts
                cluster_id += 1

        return labels, clusters_summary, sim_matrix
