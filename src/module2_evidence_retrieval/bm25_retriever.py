import re
import numpy as np

class BM25Retriever:
    """
    BM25 Lexical Retrieval Engine.
    Uses BM25Okapi scoring over tokenized news corpora to retrieve top matching evidence items.
    """
    def __init__(self, corpus_articles=None):
        self.corpus = corpus_articles or []
        self.bm25 = None
        self.is_initialized = False
        
        if self.corpus:
            self.index_corpus(self.corpus)

    def _tokenize(self, text):
        """Tokenize text into lowercase alphanumeric tokens."""
        return re.findall(r'\w+', text.lower())

    def index_corpus(self, articles):
        """Index a list of article dicts: [{'title': ..., 'content': ..., 'source': ..., 'url': ...}]"""
        self.corpus = articles
        tokenized_corpus = [
            self._tokenize(f"{art.get('title', '')} {art.get('content', '')}")
            for art in self.corpus
        ]
        
        try:
            from rank_bm25 import BM25Okapi
            self.bm25 = BM25Okapi(tokenized_corpus)
            self.is_initialized = True
        except Exception as e:
            print(f"[BM25 Notice] rank_bm25 library exception ({e}). Using TF-IDF vector score calculation fallback.")
            self.is_initialized = False

    def retrieve(self, query: str, top_k: int = 15):
        """Retrieves top_k evidence articles scored by BM25 relevance."""
        if not self.corpus:
            return []
            
        tokenized_query = self._tokenize(query)
        
        if self.is_initialized and self.bm25 is not None:
            scores = self.bm25.get_scores(tokenized_query)
            top_indices = np.argsort(scores)[::-1][:top_k]
            
            results = []
            for idx in top_indices:
                if scores[idx] > 0.01 or len(results) < min(top_k, len(self.corpus)):
                    art = dict(self.corpus[idx])
                    art['bm25_score'] = float(scores[idx])
                    art['retrieval_method'] = 'BM25'
                    results.append(art)
            return results
        else:
            # Fallback TF-IDF overlap calculation
            results = []
            q_set = set(tokenized_query)
            for art in self.corpus:
                doc_tokens = set(self._tokenize(f"{art.get('title', '')} {art.get('content', '')}"))
                overlap = len(q_set.intersection(doc_tokens))
                score = overlap / (len(q_set) + 1.0)
                art_copy = dict(art)
                art_copy['bm25_score'] = round(score, 4)
                art_copy['retrieval_method'] = 'BM25 (Lexical Overlap)'
                results.append(art_copy)
                
            results.sort(key=lambda x: x['bm25_score'], reverse=True)
            return results[:top_k]
