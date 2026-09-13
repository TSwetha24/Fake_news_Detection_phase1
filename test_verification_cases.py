import sys
sys.path.append('.')
from pipeline import ClaimVerificationPipeline

def test_full_pipeline():
    pipeline = ClaimVerificationPipeline()

    test_claims = [
        "Joseph Vijay is the CM of TamilNadu",
        "M K Stalin is the CM of TamilNadu",
        "Suriya is the CM of TamilNadu",
        "NASA says drinking lemon water would cause lung infection",
        "Tomorrow for coimbatore district due to heavy rains schools and colleges are leave on 14/8/2026"
    ]

    for claim in test_claims:
        print("="*80)
        print(f"CLAIM: {claim}")
        res = pipeline.process_claim(claim)
        print(f"FINAL VERDICT: {res['final_verdict']} | TRUST SCORE: {res['preliminary_trust_score']}%")
        print(f"RATIONALE: {res['verdict_rationale']}")
        
        scores = res["module_confidence_scores"]
        print(f"SCORES -> C1(Content): {scores['module1_content_confidence']} | C2(Evidence): {scores['module2_evidence_confidence']} | C3(Independence): {scores['module3_independence_confidence']} | C4(Agentic): {scores['module4_agentic_confidence']} | C5(Credibility): {scores['module5_credibility_confidence']}")
        
        mod4 = res["module4_agentic"]
        print(f"AGENTIC VERDICT: {mod4['agent_verdict']} | Tools Invoked ({mod4['tools_invoked_count']}): {mod4['tools_invoked']}")
        
        mod5 = res["module5_credibility"]
        print(f"SOURCE CREDIBILITY: {mod5['source_credibility_score']} | Tiers: {mod5['tier_percentages']}")
        
        mod6 = res["module6_fusion"]
        print(f"FUSION BREAKDOWN: Linear Sum={mod6['formula_breakdown']['linear_weighted_sum']}% | Logit z={mod6['formula_breakdown']['logistic_logit_z']} | Calibrated Prob={mod6['formula_breakdown']['logistic_calibrated_probability_pct']}%")

if __name__ == "__main__":
    test_full_pipeline()
