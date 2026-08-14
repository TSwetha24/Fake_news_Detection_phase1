import numpy as np
import config

class SentenceBERTEncoder:
    """
    Sentence-BERT Embedding Encoder.
    Encodes article headlines and content snippets into dense semantic vector representations
    for pairwise similarity analysis.
    """
    def __init__(self, model_name=config.SENTENCE_BERT_MODEL):
        self.model_name = model_name
        self.model = None
        self.is_sbert_available = False
        
        self._init_encoder()

    def _init_encoder(self):
        """Initializes SentenceTransformers model."""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
            self.is_sbert_available = True
        except Exception as e:
            print(f"[Sentence-BERT Notice] SentenceTransformer model notice ({e}). Using TF-IDF normalized vector space fallback.")
            self.is_sbert_available = False

    def encode_articles(self, articles):
        """
        Encodes list of article dicts into an (N, D) numpy array of normalized vector embeddings.
        """
        texts = [f"{a.get('title', '')} {a.get('content', '')}" for a in articles]
        if not texts:
            return np.array([])

        if self.is_sbert_available and self.model is not None:
            embeddings = self.model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
            return embeddings
        else:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.preprocessing import normalize
            
            tfidf = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
            X = tfidf.fit_transform(texts).toarray()
            norm_embeddings = normalize(X)
            return norm_embeddings
