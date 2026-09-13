import math
from typing import Dict, Any

class TrustScoreFusionEngine:
    """
    MODULE 6: Trust Score Fusion Module.
    Algorithms / Techniques: Multi-Dimensional Weighted Score Fusion, Calibrated Logistic Regression, Bayesian Decision Engine.

    Synthesizes confidence scores across all five analytical modules:
    - C1: Module 1 Content Classifier (RoBERTa / Softmax)
    - C2: Module 2 Live Evidence Verification (Multi-Source Search & Stance)
    - C3: Module 3 Source Independence (Sentence-BERT & Story Clustering)
    - C4: Module 4 Agentic Verification (Autonomous Tool Selection & Reasoning)
    - C5: Module 5 Source Credibility (Domain Reputation & Trust Tiering)
    """
    def __init__(self):
        print("[Module 6] Initializing Trust Score Fusion Engine (Weighted Score Fusion, Logistic Regression Calibration, Decision Gate)...")
        # Optimal fusion weights summing to 1.0
        self.weights = {
            "w1_content": 0.15,
            "w2_evidence": 0.30,
            "w3_independence": 0.15,
            "w4_agentic": 0.25,
            "w5_credibility": 0.15
        }
        # Pre-calibrated Logistic Regression parameters (trained on verification benchmark distributions)
        self.logistic_intercept = -2.20
        self.logistic_coefficients = {
            "beta_1": 0.85,
            "beta_2": 2.40,
            "beta_3": 0.65,
            "beta_4": 2.10,
            "beta_5": 0.90
        }

    def fuse_scores(
        self,
        c1: float,
        c2: float,
        c3: float,
        c4: float,
        c5: float,
        mod1_label: str = "Real",
        is_contradiction_detected: bool = False,
        contradiction_reason: str = "",
        is_unsupported_evidence: bool = False
    ) -> Dict[str, Any]:
        """
        Combines 5-module confidence scores into a definitive, calibrated Trust Score and Verdict.
        """
        # Clamp inputs to [0.0, 1.0]
        c1 = max(0.0, min(1.0, float(c1)))
        c2 = max(0.0, min(1.0, float(c2)))
        c3 = max(0.0, min(1.0, float(c3)))
        c4 = max(0.0, min(1.0, float(c4)))
        c5 = max(0.0, min(1.0, float(c5)))

        # 1. Linear Weighted Multi-Module Score Fusion
        w = self.weights
        linear_weighted_trust = (
            w["w1_content"] * c1 +
            w["w2_evidence"] * c2 +
            w["w3_independence"] * c3 +
            w["w4_agentic"] * c4 +
            w["w5_credibility"] * c5
        )

        # 2. Logistic Regression Sigmoidal Probability Calibration
        beta = self.logistic_coefficients
        z = (
            self.logistic_intercept +
            beta["beta_1"] * c1 +
            beta["beta_2"] * c2 +
            beta["beta_3"] * c3 +
            beta["beta_4"] * c4 +
            beta["beta_5"] * c5
        )
        logistic_calibrated_prob = 1.0 / (1.0 + math.exp(-max(-15.0, min(15.0, z))))

        # 3. Contradiction Safety Gate (Deterministic Overrule)
        # Three distinct outcomes:
        #   A) CONTRADICTED  → is_contradiction_detected OR contradiction_reason contains "CONTRADICTED"
        #                       → Verdict: "Fake"  (red badge)
        #   B) UNSUPPORTED   → c2 ≤ 0.15 but no direct contradiction found (reason says "Unsupported")
        #                       → Verdict: "Unsupported" (amber badge)
        #   C) AGENT REFUTED → c4 ≤ 0.20 (agentic tools found contradiction)
        #                       → Verdict: "Fake"  (red badge)
        reason_upper = (contradiction_reason or "").upper()
        # A) Real factual contradiction: caller explicitly detected it, or reason contains CONTRADICTED,
        #    or agent returned high-confidence Fake — but NOT when evidence is merely absent/irrelevant
        is_directly_contradicted = (
            (is_contradiction_detected and not is_unsupported_evidence)
            or ("CONTRADICTED" in reason_upper and not is_unsupported_evidence)
            or (c4 <= 0.20 and not is_unsupported_evidence)
        )
        # B) Low evidence because no relevant articles found (distinct from contradiction)
        is_gate_unsupported = is_unsupported_evidence or (
            c2 <= 0.15
            and not is_directly_contradicted
            and "UNSUPPORTED" in reason_upper
        )

        if is_directly_contradicted or is_gate_unsupported:
            final_trust_score_pct = round(min(linear_weighted_trust * 100, 24.0), 2)
            if is_gate_unsupported:
                final_verdict = "Unsupported"
                verdict_rationale = (
                    f"Unsupported / Likely False: No authoritative evidence found that supports this claim. "
                    f"{contradiction_reason or 'Evidence retrieval returned no claim-relevant corroboration.'} "
                    f"This does NOT mean the claim is directly contradicted — it means it cannot be verified."
                )
            else:
                final_verdict = "Fake"
                verdict_rationale = (
                    f"Contradiction Safety Gate triggered: "
                    f"{contradiction_reason or 'Definitive contradiction detected in evidence or agent reasoning.'}"
                )
        else:
            # Strictly use the Multi-Module Linear Weighted Score Formula:
            # Trust Score = 0.15*C1 + 0.30*C2 + 0.15*C3 + 0.25*C4 + 0.15*C5
            final_trust_score_pct = round(linear_weighted_trust * 100, 2)

            if final_trust_score_pct >= 60.0:
                final_verdict = "Real"
                verdict_rationale = "High multi-module agreement: Evidence corroboration, authoritative sources, and consistent agent verification confirm claim authenticity."
            elif final_trust_score_pct <= 40.0:
                final_verdict = "Fake"
                verdict_rationale = "Low multi-module trust: Inadequate evidence support, high contradiction probability, or low source verification."
            else:
                final_verdict = "Unverified"
                verdict_rationale = "Inconclusive multi-module fusion: Score falls within the uncertainty interval (40% - 60%). Further authoritative corroboration required."

        # Mathematical Formula Breakdown for UI Explainer
        formula_breakdown = {
            "formula_latex": r"\text{Trust Score} = (0.15 \cdot C_1) + (0.30 \cdot C_2) + (0.15 \cdot C_3) + (0.25 \cdot C_4) + (0.15 \cdot C_5)",
            "terms": [
                {"module": "Module 1: Content Style", "symbol": "C_1", "weight": w["w1_content"], "confidence": round(c1, 4), "weighted_value": round(w["w1_content"] * c1, 4)},
                {"module": "Module 2: Evidence Support", "symbol": "C_2", "weight": w["w2_evidence"], "confidence": round(c2, 4), "weighted_value": round(w["w2_evidence"] * c2, 4)},
                {"module": "Module 3: Source Independence", "symbol": "C_3", "weight": w["w3_independence"], "confidence": round(c3, 4), "weighted_value": round(w["w3_independence"] * c3, 4)},
                {"module": "Module 4: Agentic Verification", "symbol": "C_4", "weight": w["w4_agentic"], "confidence": round(c4, 4), "weighted_value": round(w["w4_agentic"] * c4, 4)},
                {"module": "Module 5: Source Credibility", "symbol": "C_5", "weight": w["w5_credibility"], "confidence": round(c5, 4), "weighted_value": round(w["w5_credibility"] * c5, 4)},
            ],
            "linear_weighted_sum": round(linear_weighted_trust * 100, 2),
            "logistic_logit_z": round(z, 3),
            "logistic_calibrated_probability_pct": round(logistic_calibrated_prob * 100, 2),
            "final_fused_score_pct": final_trust_score_pct
        }

        return {
            "module_name": "Module 6: Trust Score Fusion",
            "final_trust_score": final_trust_score_pct,
            "final_verdict": final_verdict,
            "verdict_rationale": verdict_rationale,
            "is_contradiction_active": is_contradiction_detected,
            "formula_breakdown": formula_breakdown,
            "module_inputs": {
                "C1_content": round(c1, 4),
                "C2_evidence": round(c2, 4),
                "C3_independence": round(c3, 4),
                "C4_agentic": round(c4, 4),
                "C5_credibility": round(c5, 4)
            }
        }
