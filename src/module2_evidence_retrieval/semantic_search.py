import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import config

class SemanticSearchRetriever:
    """
    Semantic Search Retrieval Engine.
    Uses dense vector embeddings (Sentence-BERT / Transformers) and Cosine Similarity
    to retrieve contextually relevant evidence articles beyond exact keyword matches.
    """
    def __init__(self, model_name=config.SENTENCE_BERT_MODEL):
        self.model_name = model_name
        self.model = None
        self.corpus = []
        self.corpus_embeddings = None
        self.is_ready = False
        
        self._init_encoder()

    def _init_encoder(self):
        """Attempts to load SentenceTransformer model."""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
            self.is_ready = True
        except Exception as e:
            print(f"[Semantic Search Notice] SentenceTransformer loading notice ({e}). Using TF-IDF Vector Semantic Space fallback.")
            self.is_ready = False

    def index_corpus(self, articles):
        """Generates dense embeddings for each article title + content in the corpus."""
        self.corpus = articles
        texts = [f"{a.get('title', '')} {a.get('content', '')}" for a in articles]
        
        if not texts:
            return

        if self.is_ready and self.model is not None:
            self.corpus_embeddings = self.model.encode(texts, show_progress_bar=False)
        else:
            from sklearn.feature_extraction.text import TfidfVectorizer
            self.tfidf = TfidfVectorizer(ngram_range=(1, 2), max_features=10000)
            self.corpus_embeddings = self.tfidf.fit_transform(texts).toarray()

    def retrieve(self, query: str, top_k: int = 15):
        """Retrieves top_k evidence items ranked by cosine similarity to the query embedding."""
        if not self.corpus or self.corpus_embeddings is None:
            return []

        if self.is_ready and self.model is not None:
            query_embedding = self.model.encode([query])
            sim_scores = cosine_similarity(query_embedding, self.corpus_embeddings)[0]
        else:
            query_vec = self.tfidf.transform([query]).toarray()
            sim_scores = cosine_similarity(query_vec, self.corpus_embeddings)[0]

        top_indices = np.argsort(sim_scores)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            art = dict(self.corpus[idx])
            art['semantic_score'] = float(sim_scores[idx])
            art['retrieval_method'] = 'Semantic Search (Vector Embeddings)'
            results.append(art)

        return results
