import json
from pipeline import ClaimVerificationPipeline

p = ClaimVerificationPipeline()
claim = "cm vijay to arrive in coimbatore on 16th August"
res = p.process_claim(claim)
articles = res['module2_retrieval'].get('evidence_items', [])
print(f"Total retrieved articles: {len(articles)}")
print(f"Final verdict: {res.get('final_verdict')}")
print(f"Preliminary trust score: {res.get('preliminary_trust_score')}")
print(f"Verdict rationale: {res.get('verdict_rationale')}")

for i, a in enumerate(articles[:10]):
    print(f"\n--- Article {i+1} ---")
    print("Title:", a.get("title"))
    print("Publish Date:", a.get("publish_date"))
    print("Relevance:", a.get("relevance_score"))
    print("Stance:", a.get("stance"))
    print("Entity/Role Status:", a.get("entity_role_status"))
    print("Date Match Status:", a.get("date_match_status"))
    print("Content snippet:", (a.get("content") or "")[:120])
