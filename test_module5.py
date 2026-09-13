import sys
sys.path.append('.')
from src.module5_source_credibility.evaluator import SourceCredibilityEvaluator

evaluator = SourceCredibilityEvaluator()

sample_evidence = [
    {'title': 'Tamil Nadu CM Vijay unveils package', 'domain': 'thehindu.com', 'url': 'https://thehindu.com', 'relevance_score': 0.95},
    {'title': 'PTI: Chief Minister Vijay announces scheme', 'domain': 'reuters.com', 'url': 'https://reuters.com', 'relevance_score': 0.95},
    {'title': 'Wikipedia: Chief Ministers of Tamil Nadu', 'domain': 'en.wikipedia.org', 'url': 'https://en.wikipedia.org', 'relevance_score': 0.90},
    {'title': 'Entertainment report on TN leaders', 'domain': 'pinkvilla.com', 'url': 'https://pinkvilla.com', 'relevance_score': 0.40}
]

res = evaluator.evaluate(sample_evidence)
print("="*60)
print("MODULE 5 EVALUATION RESULTS")
print("Composite Credibility Score (C5):", res["source_credibility_score"])
print("Tier Distribution:", res["tier_counts"])
print("Tier Percentages:", res["tier_percentages"])
for s in res["evaluated_sources"]:
    print(f" - {s['publisher_name']} ({s['domain']}): {s['tier']} | Score: {s['credibility_score']} | Factuality: {s['factuality']}")
