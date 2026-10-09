import re
from typing import Dict, Any, List
from src.module5_source_credibility.reputation_db import (
    DOMAIN_REPUTATION_DATABASE,
    DEFAULT_REPUTATION_PROFILE
)

class SourceCredibilityEvaluator:
    """
    MODULE 5: Source Credibility Assessment Module.
    Algorithms / Techniques: Domain Reputation Lookup, Credibility Scoring, Publisher Tiering.

    Evaluates the credibility of every retrieved evidence source, assessing factuality ratings,
    editorial standards, and bias taxonomy to produce a composite Credibility Score (C5).
    """
    def __init__(self):
        print("[Module 5] Initializing Source Credibility Evaluator (Domain Reputation DB, NewsGuard/MBFC Taxonomy, Tier Scoring)...")
        self.reputation_db = DOMAIN_REPUTATION_DATABASE

    def evaluate(self, evidence_articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluates a list of retrieved evidence articles and computes the composite credibility score (C5).
        """
        if not evidence_articles:
            return {
                "module_name": "Module 5: Source Credibility Assessment",
                "source_credibility_score": 0.50,
                "tier_distribution": {"tier1": 0, "tier2": 0, "tier3": 0, "tier4": 0},
                "tier_percentages": {"tier1_pct": 0, "tier2_pct": 0, "tier3_pct": 0, "tier4_pct": 0},
                "evaluated_sources": []
            }

        evaluated_articles = []
        tier_counts = {"Tier 1": 0, "Tier 2": 0, "Tier 3": 0, "Tier 4": 0}
        total_weight = 0.0
        weighted_score_sum = 0.0

        for art in evidence_articles:
            raw_source = art.get("source", "")
            raw_domain = art.get("domain", "").lower().replace("http://", "").replace("https://", "").split("/")[0]
            if raw_domain.startswith("www."):
                raw_domain = raw_domain[4:]

            # Un-wrap Google News wrapper if present: "Google News (Nagaland Post)" -> "Nagaland Post"
            clean_pub_name = raw_source.replace("Google News (", "").rstrip(")").strip()
            if not clean_pub_name:
                clean_pub_name = raw_domain

            # Lookup domain or source name in reputation DB
            profile = None
            if raw_domain in self.reputation_db:
                profile = self.reputation_db[raw_domain]
            else:
                clean_lower = clean_pub_name.lower()
                for key, val in self.reputation_db.items():
                    key_name = val.get("name", "").lower()
                    domain_name = key.replace(".com", "").replace(".in", "").replace(".co.uk", "").replace(".org", "")
                    if (domain_name and domain_name in raw_domain) or (domain_name and domain_name in clean_lower) or (clean_lower and clean_lower in key_name):
                        profile = val
                        break

            if profile is None:
                # Dynamic fallback based on clean_pub_name
                lower = clean_pub_name.lower()
                if any(k in lower for k in ["hindu", "reuters", "ap news", "bbc", "pti", "pib", "nature", "wikipedia"]):
                    profile = {
                        "name": clean_pub_name,
                        "tier": "Tier 1: Highly Authoritative",
                        "credibility_score": 0.95,
                        "factuality": "HIGH FACTUALITY",
                        "bias": "LEAST BIASED",
                        "description": "Primary institutional wire & record-of-fact publisher."
                    }
                elif any(k in lower for k in ["times", "express", "ndtv", "today", "mint", "print", "quint", "news18", "guardian"]):
                    profile = {
                        "name": clean_pub_name,
                        "tier": "Tier 2: Mainstream Credible",
                        "credibility_score": 0.84,
                        "factuality": "GENERAL REPORTING",
                        "bias": "CENTER",
                        "description": "Established commercial national news outlet."
                    }
                else:
                    profile = {
                        "name": clean_pub_name,
                        "tier": "Tier 3: Regional / Independent",
                        "credibility_score": 0.72,
                        "factuality": "REGIONAL REPORTING",
                        "bias": "LOCAL PRESS",
                        "description": "Regional state daily or local publication with localized editorial focus."
                    }

            cred_score = profile["credibility_score"]
            tier_name = profile["tier"].split(":")[0].strip()
            if tier_name in tier_counts:
                tier_counts[tier_name] += 1
            else:
                tier_counts["Tier 2"] += 1

            # Weight by article relevance
            relevance = art.get("relevance_score", 0.5)
            weight = max(0.1, relevance)
            weighted_score_sum += (cred_score * weight)
            total_weight += weight

            evaluated_articles.append({
                "title": art.get("title", ""),
                "domain": raw_domain,
                "publisher_name": profile["name"],
                "tier": profile["tier"],
                "credibility_score": cred_score,
                "factuality": profile["factuality"],
                "bias": profile["bias"],
                "url": art.get("url", "#"),
                "relevance": relevance,
                "description": profile["description"]
            })

        # Calculate composite credibility score C5
        if total_weight > 0:
            composite_c5 = round(weighted_score_sum / total_weight, 4)
        else:
            composite_c5 = 0.75

        total_sources = len(evaluated_articles)
        tier_percentages = {
            "tier1_pct": round((tier_counts["Tier 1"] / float(total_sources)) * 100, 1),
            "tier2_pct": round((tier_counts["Tier 2"] / float(total_sources)) * 100, 1),
            "tier3_pct": round((tier_counts["Tier 3"] / float(total_sources)) * 100, 1),
            "tier4_pct": round((tier_counts["Tier 4"] / float(total_sources)) * 100, 1),
        }

        return {
            "module_name": "Module 5: Source Credibility Assessment",
            "source_credibility_score": composite_c5,
            "total_sources_evaluated": total_sources,
            "tier_counts": tier_counts,
            "tier_percentages": tier_percentages,
            "evaluated_sources": evaluated_articles
        }
