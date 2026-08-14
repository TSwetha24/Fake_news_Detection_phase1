import sys
import unittest
from data_loader import load_fakeddit_dataset
from src.module1_fake_news_detection.detector import FakeNewsDetector
from src.module2_evidence_retrieval.retriever import EvidenceRetriever
from src.module3_source_independence.analyzer import SourceIndependenceAnalyzer
from pipeline import ClaimVerificationPipeline

class TestFakeNewsModules(unittest.TestCase):

    def test_01_fakeddit_data_loader(self):
        print("\n--- Testing Fakeddit Data Loader ---")
        df = load_fakeddit_dataset()
        self.assertGreater(len(df), 0, "Dataset should not be empty")
        self.assertIn("clean_title", df.columns)
        self.assertIn("label_name", df.columns)
        print(f"PASS: Successfully loaded Fakeddit dataset with {len(df)} samples.")

    def test_02_module1_fake_news_detection(self):
        print("\n--- Testing Module 1: Fake News Detection (RoBERTa / Softmax) ---")
        detector = FakeNewsDetector()
        res = detector.predict("NASA James Webb Telescope discovers exoplanet atmosphere")
        self.assertIn("label", res)
        self.assertIn(res["label"], ["Real", "Fake", "Unverified"])
        self.assertGreaterEqual(res["confidence_score"], 0.0)
        self.assertLessEqual(res["confidence_score"], 1.0)
        print(f"PASS: Module 1 output: Label={res['label']}, Confidence={res['confidence_score']}, Probabilities={res['probabilities']}")

    def test_03_module2_evidence_retrieval(self):
        print("\n--- Testing Module 2: Evidence Retrieval (15+ Articles) ---")
        retriever = EvidenceRetriever()
        res = retriever.retrieve_evidence("5G towers memory loss claim", target_count=15)
        self.assertGreaterEqual(res["total_articles_retrieved"], 15, "Should retrieve at least 15 evidence articles")
        self.assertEqual(len(res["evidence_items"]), res["total_articles_retrieved"])
        print(f"PASS: Module 2 retrieved {res['total_articles_retrieved']} evidence articles using {res['backends_used']}.")

    def test_04_module3_source_independence(self):
        print("\n--- Testing Module 3: Source Independence Analysis (Sentence-BERT & Clustering) ---")
        analyzer = SourceIndependenceAnalyzer()
        articles = [
            {"title": "NASA James Webb space telescope water vapor discovery", "domain": "nasa.gov", "source": "NASA"},
            {"title": "NASA James Webb space telescope water vapor discovery", "domain": "reuters.com", "source": "Reuters"},
            {"title": "Deep ocean current discovery", "domain": "nature.com", "source": "Nature"}
        ]
        res = analyzer.analyze(articles)
        self.assertEqual(res["total_articles_analyzed"], 3)
        self.assertGreater(res["independent_sources_count"], 0)
        self.assertGreaterEqual(res["source_independence_score"], 0.0)
        print(f"PASS: Module 3 clusters={res['independent_sources_count']}, Independence Score={res['source_independence_score']}")

    def test_05_end_to_end_pipeline(self):
        print("\n--- Testing End-to-End Pipeline (Modules 1, 2, 3) ---")
        pipeline = ClaimVerificationPipeline()
        res = pipeline.process_claim("Global renewable energy capacity grew by a record 50% in 2023", target_evidence_count=15)
        self.assertIn("module1_detection", res)
        self.assertIn("module2_retrieval", res)
        self.assertIn("module3_independence", res)
        self.assertGreaterEqual(res["module2_retrieval"]["total_articles_retrieved"], 15)
        print(f"PASS: End-to-End verification complete in {res['execution_time_seconds']}s with Trust Score {res['preliminary_trust_score']}%.")

if __name__ == "__main__":
    unittest.main()
