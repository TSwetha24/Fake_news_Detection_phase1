import json
import datetime
from pipeline import ClaimVerificationPipeline
from date_utils import extract_target_dates
import config

p = ClaimVerificationPipeline()

test_claims = [
    "Joseph Vijay is the CM of TamilNadu",
    "M K Stalin is the CM of TamilNadu",
    "Suriya is the CM of TamilNadu",
    "NASA says drinking lemon water would cause lung infection",
    "Tomorrow for coimbatore district due to heavy rains schools and colleges are leave on 14/8/2026",
    "cm vijay to arrive in coimbatore on 16th August",
    "Global renewable energy capacity grew by a record 50% in 2023, report finds"
]

print("=" * 80)
print("DIAGNOSIS ON CANONICAL TEST CLAIMS (STEP 1)")
print("=" * 80)

for idx, claim in enumerate(test_claims):
    print(f"\n[{idx+1}/{len(test_claims)}] CLAIM: '{claim}'")
    
    # Date and Class
    d_info = extract_target_dates(claim)
    has_date = d_info.get("is_date_specific_claim", False)
    target_date = d_info.get("target_date_iso", None)
    
    # Classify PAST / TODAY / UPCOMING / TIMELESS
    now_date = datetime.date.today()
    if not has_date or not target_date:
        date_class = "TIMELESS"
    elif target_date < now_date:
        date_class = "PAST"
    elif target_date == now_date:
        date_class = "TODAY"
    else:
        date_class = "UPCOMING"
        
    print(f"  Claim Date: {target_date or 'None'} | Class: {date_class}")
    
    # Run verification (pipeline only, no blockchain write)
    res = p.process_claim(claim)
    
    retrieval = res.get("module2_retrieval", {})
    evidence_items = retrieval.get("evidence_items", [])
    print(f"  Articles Retrieved: {len(evidence_items)}")
    
    # Check freshness window (e.g. 7 days / within date window)
    in_window_count = 0
    for a in evidence_items:
        p_date = a.get("publish_date", "")
        if "2026" in p_date or "Live" in p_date or "Verified" in p_date:
            in_window_count += 1
    print(f"  Articles in Freshness Window: {in_window_count}")
    
    # Sources that failed and why
    backends = retrieval.get("backends_used", [])
    # Check retriever instance sources status
    print(f"  Sources Summary: {retrieval.get('sources_responded_summary', 'Unknown')}")
    
    # Stances for first 3 articles
    print("  Per-Article Stance Sample (First 3):")
    for i, a in enumerate(evidence_items[:3]):
        st = a.get("stance", "None")
        er = a.get("entity_role_status", "None")
        dm = a.get("date_match_status", "None")
        print(f"    - Art {i+1}: '{a.get('title', '')[:50]}...' | Stance: {st} | Role: {er} | Date: {dm}")
        
    scores = res.get("module_confidence_scores", {})
    c1 = scores.get("module1_content_confidence")
    c2 = scores.get("module2_evidence_confidence")
    c3 = scores.get("module3_independence_confidence")
    c4 = scores.get("module4_agentic_confidence")
    c5 = scores.get("module5_credibility_confidence")
    print(f"  C1..C5: C1={c1}, C2={c2}, C3={c3}, C4={c4}, C5={c5}")
    
    trust = res.get("preliminary_trust_score")
    verdict = res.get("final_verdict")
    badge = res.get("badge_label")
    m6 = res.get("module6_fusion", {})
    p_real = m6.get("p_real", trust)
    print(f"  Verdict: {verdict} | Badge: {badge} | Trust Score: {trust}% | P(Real): {p_real}%")
    print(f"  Rationale: {res.get('verdict_rationale')}")
    
    # Developing Story check
    rel_cnt = len([a for a in evidence_items if a.get("relevance_score", 0) >= 0.35])
    if badge == "Unverified - Developing Story":
        print(f"  Exact condition for 'Developing Story': relevant_articles_count ({rel_cnt}) < 3 and not contradicted.")
    elif badge == "Unverified - Upcoming Event":
        print(f"  Exact condition for 'Upcoming Event': is_date_claim=True, is_future_or_today=True, not contradicted.")
