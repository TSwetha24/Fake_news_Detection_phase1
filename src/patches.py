import os
import re
import math
import datetime
import urllib.parse
from typing import Dict, Any, List, Optional, Tuple
import config

# Standard common stopwords for search keyword extraction
STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "can't", "cannot", "could",
    "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down",
    "during", "each", "few", "for", "from", "further", "had", "hadn't", "has",
    "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her",
    "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's",
    "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it",
    "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my",
    "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or",
    "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same",
    "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so",
    "some", "such", "than", "that", "that's", "the", "their", "theirs", "them",
    "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll",
    "they're", "they've", "this", "those", "through", "to", "too", "under",
    "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're",
    "we've", "were", "weren't", "what", "what's", "when", "when's", "where",
    "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with",
    "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've",
    "your", "yours", "yourself", "yourselves", "says", "claim", "claims", "announced"
}

# ==============================================================================
# F1: Rule Scoping Logic
# ==============================================================================
def is_topic_rule_applicable(rule_name: str, claim: str) -> bool:
    """
    F1: Scopes topic-specific rules strictly to their domain keywords.
    A date alone MUST NEVER trigger a topic-specific rule.
    """
    if not getattr(config, "ENABLE_RULE_SCOPING_PATCH", True):
        return True  # Revert to old behavior if flag is disabled

    claim_lower = claim.lower()

    if rule_name == "rain_holiday":
        # Requires weather keywords AND institution/holiday keywords
        has_weather = any(w in claim_lower for w in [
            "rain", "rains", "cyclone", "monsoon", "flood", "floods",
            "weather", "storm", "downpour", "inundation"
        ])
        has_holiday = any(w in claim_lower for w in [
            "holiday", "holidays", "leave", "schools", "colleges",
            "school", "college", "closure", "declared holiday", "shut"
        ])
        return has_weather and has_holiday

    elif rule_name == "cross_domain":
        # Requires space agency + medical/health topic, or state + prime minister
        space_agencies = ["nasa", "isro", "esa", "spacex", "jaxa", "cnsa"]
        health_topics = [
            "lemon", "lung", "infection", "cure", "cancer", "vaccine",
            "diet", "drinking", "medicine", "covid", "virus", "treatment"
        ]
        has_space = any(sa in claim_lower for sa in space_agencies)
        has_health = any(ht in claim_lower for ht in health_topics)
        is_state_pm = any(w in claim_lower for w in ["prime minister of", "pm of"]) and any(
            st in claim_lower for st in ["tamil nadu", "tamilnadu", "kerala", "karnataka", "andhra", "delhi"]
        )
        return (has_space and has_health) or is_state_pm

    elif rule_name == "medical":
        # Requires biomedical / health topic keywords
        return any(w in claim_lower for w in [
            "fast food", "fast foods", "junk food", "lung", "respiratory",
            "cure", "treat", "heal", "chickenpox", "vaccine", "infection"
        ])

    return True


# ==============================================================================
# F2 & F3: Upcoming Events & Developing Stories
# ==============================================================================
def evaluate_event_recency_verdict(
    claim: str,
    date_info: Dict[str, Any],
    is_directly_contradicted: bool,
    linear_weighted_trust: float,
    relevant_articles_count: int = 0
) -> Optional[Tuple[float, str, str, str]]:
    """
    F2 & F3: Evaluates upcoming events and developing stories.
    Returns (calibrated_trust_score, verdict, badge_label, rationale) if applicable, else None.
    """
    if is_directly_contradicted:
        return None

    if getattr(config, "ENABLE_TWO_VERDICTS_ONLY", False):
        return None

    # F2: Upcoming Events (Target date is today or in the future)
    if getattr(config, "ENABLE_UPCOMING_EVENT_PATCH", True):
        is_date_claim = date_info.get("is_date_specific_claim", False)
        is_future_or_today = date_info.get("is_future_or_today", False)
        if is_date_claim and is_future_or_today:
            # Calibrated trust in the unverified / pending range (~48-58%)
            calibrated_score = round(max(45.0, min(58.0, linear_weighted_trust * 100)), 2)
            target_str = date_info.get("target_date_str_readable", "the scheduled date")
            rationale = (
                f"Unverified - Upcoming Event: Claim references a scheduled or upcoming event on {target_str}. "
                "No authoritative refutation, institutional denial, or factual contradiction detected across verified news wires."
            )
            return calibrated_score, "Unverified", "Unverified - Upcoming Event", rationale

    # F3: Developing Stories (Few relevant articles, fresh or time-sensitive, no contradiction)
    if getattr(config, "ENABLE_DEVELOPING_STORY_PATCH", True):
        if relevant_articles_count < 3:
            calibrated_score = round(max(42.0, min(54.0, linear_weighted_trust * 100)), 2)
            rationale = (
                "Unverified - Developing Story: Limited initial live reporting currently available (<3 corroborated articles). "
                "No factual contradiction, entity mismatch, or official debunking detected across official sources."
            )
            return calibrated_score, "Unverified", "Unverified - Developing Story", rationale

    return None


# ==============================================================================
# F4: Contradiction Gate Score Scaling
# ==============================================================================
def compute_gate_score(linear_weighted_trust: float, cap: float = 24.0) -> float:
    """
    F4: Computes the gated trust score strictly below the <=24% cap.
    Scales proportionally so different module confidence vectors produce real score variations.
    """
    if not getattr(config, "ENABLE_GATE_SCORE_SCALING_PATCH", True):
        return round(min(linear_weighted_trust * 100, cap), 2)

    # Proportional scaling below cap: linear_weighted_trust (0.0 to 1.0) maps to (0.0 to 24.0)
    # E.g. 0.32 -> 7.68%, 0.50 -> 12.00%, 0.80 -> 19.20%
    scaled = round(linear_weighted_trust * cap, 2)
    return min(scaled, cap)


# ==============================================================================
# F5: Strict Cache Key Matching with Dates, Named Entities, and TTL
# ==============================================================================
def extract_claim_entities(claim_text: str) -> List[str]:
    """Extracts distinctive named entities and proper nouns from a claim."""
    tokens = re.findall(r'\b[A-Za-z0-9]+\b', claim_text)
    entities = []
    for t in tokens:
        t_lower = t.lower()
        if t_lower not in STOPWORDS and len(t) >= 3:
            entities.append(t_lower)
    return entities


def is_time_sensitive_claim(claim_text: str) -> bool:
    """Detects if a claim mentions temporal dates, today, tomorrow, or real-time breaking events."""
    claim_lower = claim_text.lower()
    time_markers = [
        "today", "tomorrow", "yesterday", "tonight", "this morning",
        "breaking", "latest", "cancelled", "holiday", "rains", "leave", "arrive", "visit"
    ]
    if any(m in claim_lower for m in time_markers):
        return True
    if re.search(r'\b\d{1,2}[/\.-]\d{1,2}[/\.-]\d{2,4}\b', claim_text):
        return True
    if re.search(r'\b\d{1,2}(?:st|nd|rd|th)?\s+(?:january|february|march|april|may|june|july|august|september|october|november|december)\b', claim_lower):
        return True
    return False


def is_strict_cache_match(
    search_claim: str,
    block: Any,
    sim_score: float = 0.0,
    similarity_threshold: float = 0.88
) -> Tuple[bool, float]:
    """
    F5: Strict cache matching logic with entity separation, date preservation, and TTL validation.
    """
    search_norm = search_claim.strip().lower()
    block_norm = block.claim.strip().lower()

    # 0. Pipeline Version Check: ignore blocks whose pipeline_version differs from current or is missing
    current_version = getattr(config, "PIPELINE_VERSION", "2.0.0")
    block_vdata = getattr(block, "verification_data", {}) or {}
    block_version = block_vdata.get("pipeline_version")
    if block_version != current_version:
        return False, 0.0

    # 1. Date Compatibility Check: claims with different dates must never match
    from date_utils import extract_target_dates
    d_search = extract_target_dates(search_claim)
    d_block = extract_target_dates(block.claim)
    if d_search.get("is_date_specific_claim") != d_block.get("is_date_specific_claim"):
        return False, 0.0
    if d_search.get("is_date_specific_claim") and d_block.get("is_date_specific_claim"):
        if d_search.get("target_date_str_iso") != d_block.get("target_date_str_iso"):
            return False, 0.0

    # 2. TTL Check (Time-to-Live): expires time-sensitive claims after configured TTL
    if getattr(config, "ENABLE_CACHE_TTL_PATCH", True):
        is_time_sens = is_time_sensitive_claim(search_claim) or is_time_sensitive_claim(block.claim)
        ttl_limit = getattr(config, "CACHE_TTL_HOURS_TIME_SENSITIVE", 6.0) if is_time_sens else getattr(config, "CACHE_TTL_HOURS_GENERAL", 24.0)

        try:
            ts_str = block.timestamp.rstrip("Z")
            if "." in ts_str:
                block_time = datetime.datetime.fromisoformat(ts_str)
            else:
                block_time = datetime.datetime.strptime(ts_str, "%Y-%m-%dT%H:%M:%S")

            now_utc = datetime.datetime.now(datetime.timezone.utc)
            if block_time.tzinfo is None:
                block_time = block_time.replace(tzinfo=datetime.timezone.utc)

            age_hours = (now_utc - block_time).total_seconds() / 3600.0
            if age_hours > ttl_limit:
                # Expired cache entry -> re-verify
                return False, 0.0
        except Exception:
            pass

    # Exact string or hash match
    is_exact = (search_norm == block_norm or block.claim_hash == block.hash_claim(search_claim))
    if is_exact:
        return True, 1.0

    # 3. Entity Difference Check (Prevent 'stalin' matching 'vijay' or different entities)
    if getattr(config, "ENABLE_STRICT_CACHE_KEY_PATCH", True):
        entities_search = set(extract_claim_entities(search_claim))
        entities_block = set(extract_claim_entities(block.claim))

        # Check for conflicting entities
        if not entities_search.issubset(entities_block) and not entities_block.issubset(entities_search):
            overlap = len(entities_search.intersection(entities_block))
            union = len(entities_search.union(entities_block))
            if union > 0 and (overlap / union) < 0.70:
                return False, 0.0

        if sim_score >= similarity_threshold:
            return True, sim_score
    else:
        if sim_score >= 0.65:
            return True, sim_score

    return False, 0.0


# ==============================================================================
# F6: Module Failure Renormalization
# ==============================================================================
def renormalize_weights_if_failed(
    module_scores: Dict[str, Optional[float]],
    configured_weights: Dict[str, float]
) -> Tuple[Dict[str, float], float, Dict[str, Any]]:
    """
    F6: If a module fails, mark it as 'module_failed' / N/A and renormalize
    remaining module weights for this request only.
    """
    if not getattr(config, "ENABLE_MODULE_FAILURE_RENORM_PATCH", True):
        total = sum(configured_weights.get(k, 0.0) * (module_scores.get(k) or 0.0) for k in configured_weights)
        return configured_weights, total, {}

    active_weights = {}
    active_scores = {}
    failed_modules = []

    for k, score in module_scores.items():
        if score is not None and score >= 0.0:
            active_weights[k] = configured_weights.get(k, 0.20)
            active_scores[k] = score
        else:
            failed_modules.append(k)

    total_active_weight = sum(active_weights.values())
    renormalized_weights = {}
    if total_active_weight > 0:
        for k, w in active_weights.items():
            renormalized_weights[k] = round(w / total_active_weight, 4)
    else:
        renormalized_weights = dict(configured_weights)

    linear_sum = sum(renormalized_weights[k] * active_scores[k] for k in active_scores)

    metadata = {
        "failed_modules": failed_modules,
        "renormalized_weights": renormalized_weights,
        "is_renormalized": len(failed_modules) > 0
    }
    return renormalized_weights, linear_sum, metadata


# ==============================================================================
# F7: Latest News Retrieval with Query Variants
# ==============================================================================
def generate_query_variants(claim: str, max_words: int = 6) -> List[str]:
    """
    F7: Extracts salient named entities and action keywords to generate 2-3 query variants.
    Prevents empty search results caused by sending full sentences.
    """
    if not getattr(config, "ENABLE_KEYWORD_SEARCH_PATCH", True):
        return [claim]

    tokens = re.findall(r'[a-zA-Z0-9]+(?:[/\.-][a-zA-Z0-9]+)*', claim)
    meaningful = [
        t.strip(".,;:?!'\"()[]{}") for t in tokens
        if t.strip(".,;:?!'\"()[]{}").lower() not in STOPWORDS
    ]

    variants = []

    # Variant 1: Key entity tokens + verbs (first 4-6 meaningful words)
    if len(meaningful) >= 2:
        variants.append(" ".join(meaningful[:max_words]))

    # Variant 2: Essential subject and location/topic (first 2-3 words)
    if len(meaningful) >= 3:
        variants.append(" ".join(meaningful[:3]))

    # Variant 3: Cleaned version without leading prepositions
    if len(meaningful) > 4:
        variants.append(" ".join(meaningful[1:5]))

    if not variants:
        variants.append(claim)

    return list(dict.fromkeys(variants))[:3]


def extract_search_keywords(query: str, max_words: int = 8) -> str:
    """Extracts top search keywords from query."""
    variants = generate_query_variants(query, max_words=max_words)
    return variants[0] if variants else query


def build_recency_query(query: str, backend: str) -> str:
    """F7: Appends recency filter parameters per backend."""
    if not getattr(config, "ENABLE_RECENCY_RETRIEVAL_PATCH", True):
        return query

    query_lower = query.lower()
    is_recent_or_breaking = any(w in query_lower for w in ["today", "yesterday", "tomorrow", "breaking", "urgent", "recent", "live", "arrive", "visit"])

    if backend == "google_news":
        time_filter = "when:3d" if is_recent_or_breaking else "when:7d"
        if "when:" not in query:
            return f"{query} {time_filter}"

    return query


def rank_and_deduplicate_articles(
    raw_articles: List[Dict[str, Any]],
    claim_query: str,
    target_count: int = 15
) -> List[Dict[str, Any]]:
    """
    F7: Combines and ranks live retrieved articles using keyword overlap, BM25, and semantic scores.
    """
    if not raw_articles:
        return []

    query_words = set(re.findall(r'\b\w{3,}\b', claim_query.lower())) - STOPWORDS
    scored = []

    for idx, art in enumerate(raw_articles):
        art_copy = dict(art)
        title = art_copy.get("title", "").lower()
        content = art_copy.get("content", "").lower()
        text = f"{title} {content}"

        matches = sum(1 for w in query_words if w in text)
        overlap = matches / float(max(1, len(query_words)))

        is_generic = "General News and Public Information Bulletin" in art_copy.get("title", "")
        base_priority = 0.0 if is_generic else 0.40

        score = base_priority + (overlap * 0.60)
        art_copy["rank_score"] = round(score, 3)
        scored.append((score, idx, art_copy))

    scored.sort(key=lambda x: (x[0], -x[1]), reverse=True)
    return [item[2] for item in scored[:target_count]]


# ==============================================================================
# F8: Dynamic UTC Date Handling
# ==============================================================================
def get_reference_date(provided_date: Optional[datetime.date] = None) -> datetime.date:
    """F8: Returns current dynamic UTC date for relative-date logic."""
    if provided_date is not None:
        return provided_date

    if getattr(config, "ENABLE_DYNAMIC_UTC_DATE_PATCH", True):
        return datetime.datetime.now(datetime.timezone.utc).date()
    else:
        return datetime.date(2026, 8, 13)


def sanitize_module1_fallback(
    claim_text: str,
    probs_dict: Dict[str, float],
    pred_label: str,
    confidence: float
) -> Tuple[str, float, Dict[str, float]]:
    """F6: Removes constant hardcoded fallback values in Module 1."""
    if not getattr(config, "ENABLE_REMOVE_CONSTANT_FALLBACKS_PATCH", True):
        return "Real", 0.72, {"Real": 0.72, "Fake": 0.15, "Unverified": 0.13}

    if probs_dict:
        best_label = max(probs_dict, key=probs_dict.get)
        best_conf = float(probs_dict[best_label])
        return best_label, best_conf, probs_dict

    return pred_label, confidence, probs_dict


def evaluate_breaking_news_verdict(
    c2: float,
    is_unsupported_evidence: bool,
    is_directly_contradicted: bool,
    linear_weighted_trust: float,
    contradiction_reason: str,
    claim_text: str = ""
) -> Optional[Tuple[float, str, str]]:
    """Legacy helper maintained for backward compatibility."""
    if not getattr(config, "ENABLE_BREAKING_NEWS_UNVERIFIED_GATE_PATCH", True):
        return None

    if getattr(config, "ENABLE_TWO_VERDICTS_ONLY", False):
        return None

    if is_unsupported_evidence and not is_directly_contradicted:
        calibrated_score = round(max(42.0, min(55.0, linear_weighted_trust * 100)), 2)
        verdict = "Unverified"
        rationale = (
            "Unverified / Developing Story: Limited live reporting currently available (<3 corroborated articles). "
            "No factual contradiction, entity mismatch, or official debunking detected across official sources."
        )
        return calibrated_score, verdict, rationale

    return None


def log_exception(context: str, err: Exception) -> None:
    """Logs caught exceptions cleanly without breaking control flow."""
    if getattr(config, "ENABLE_LOGGED_EXCEPTIONS_PATCH", True):
        if os.getenv("DEBUG_TRACE"):
            print(f"[{context} Notice] Caught exception: {err}")


# ==============================================================================
# Extended Role & Entity Entailment Checkers
# ==============================================================================
def patch_extract_claim_spo(claim_text: str) -> dict:
    """
    Generalized extraction of Subject, Role, and Jurisdiction from claims.
    Supports CM, PM, and all Union/Cabinet Ministerial portfolios:
    e.g. Finance Minister, Home Minister, Defence Minister, Railway Minister, President, Governor.
    """
    if not getattr(config, "ENABLE_EXTENDED_ROLE_VERIFICATION_PATCH", True):
        return {}

    claim_lower = claim_text.lower().strip()
    
    role_patterns = [
        ("finance minister", r'\b(?:finance minister|fm)\b'),
        ("home minister", r'\b(?:home minister|hm)\b'),
        ("defence minister", r'\b(?:defence minister|defense minister)\b'),
        ("external affairs minister", r'\b(?:external affairs minister|foreign minister)\b'),
        ("railway minister", r'\b(?:railway minister|railways minister)\b'),
        ("education minister", r'\b(?:education minister|hrd minister)\b'),
        ("health minister", r'\b(?:health minister)\b'),
        ("president", r'\bpresident\b'),
        ("governor", r'\bgovernor\b'),
        ("vice president", r'\bvice president\b'),
        ("chief minister", r'\b(?:chief minister|cm)\b'),
        ("prime minister", r'\b(?:prime minister|pm)\b'),
    ]
    
    detected_role = None
    for r_name, r_pat in role_patterns:
        if re.search(r_pat, claim_lower):
            detected_role = r_name
            break

    if not detected_role:
        return {}
            
    detected_jurisdiction = "india"
    if any(j in claim_lower for j in ["tamil nadu", "tamilnadu", "tn"]):
        detected_jurisdiction = "tamil nadu"
    elif "kerala" in claim_lower:
        detected_jurisdiction = "kerala"
    elif "karnataka" in claim_lower:
        detected_jurisdiction = "karnataka"
    elif "delhi" in claim_lower:
        detected_jurisdiction = "delhi"
        
    m = re.search(r'^\s*([a-zA-Z\s\.\-]+?)\s+(?:is|serves as|appointed as|was elected|became|sworn in as)\s+(?:the\s+)?(.+)$', claim_text, re.IGNORECASE)
    subject = m.group(1).strip() if m else None
    
    return {
        "subject": subject.lower() if subject else None,
        "subject_display": subject if subject else "",
        "role": detected_role,
        "jurisdiction": detected_jurisdiction,
        "is_role_claim": bool(detected_role and detected_jurisdiction and subject)
    }


def patch_analyze_extended_roles(claim: str, evidence_articles: list, base_res: dict) -> dict:
    """
    Evaluates factual office and biographical role assertions for ministerial portfolios.
    Detects when sports personalities (Sachin Tendulkar, Virat Kohli, MS Dhoni, etc.)
    or actors are claimed to hold government cabinet offices.
    """
    if not getattr(config, "ENABLE_EXTENDED_ROLE_VERIFICATION_PATCH", True):
        return base_res

    spo = patch_extract_claim_spo(claim)
    if not spo.get("is_role_claim"):
        return base_res

    role = spo["role"]
    subj = spo["subject"].lower()
    subj_display = spo["subject_display"]
    jurisdiction = spo["jurisdiction"]

    KNOWN_UNION_MINISTERS = {
        "finance minister": {
            "incumbent": "Nirmala Sitharaman",
            "aliases": ["nirmala sitharaman", "sitharaman"],
            "disqualified_sports": ["sachin tendulkar", "sachin", "tendulkar", "virat kohli", "ms dhoni", "dhoni", "rohit sharma"],
            "disqualified_actors": ["suriya", "rajinikanth", "kamal haasan", "vijay", "dhanush"]
        },
        "home minister": {
            "incumbent": "Amit Shah",
            "aliases": ["amit shah", "shah"],
            "disqualified_sports": ["sachin tendulkar", "sachin", "tendulkar", "virat kohli", "ms dhoni"],
            "disqualified_actors": ["suriya", "rajinikanth", "kamal haasan", "vijay"]
        },
        "defence minister": {
            "incumbent": "Rajnath Singh",
            "aliases": ["rajnath singh", "rajnath"],
            "disqualified_sports": ["sachin tendulkar", "sachin", "tendulkar", "virat kohli", "ms dhoni"],
            "disqualified_actors": ["suriya", "rajinikanth", "kamal haasan", "vijay"]
        },
        "prime minister": {
            "incumbent": "Narendra Modi",
            "aliases": ["narendra modi", "modi"],
            "disqualified_sports": ["sachin tendulkar", "sachin", "tendulkar", "virat kohli", "ms dhoni"],
            "disqualified_actors": ["suriya", "rajinikanth", "kamal haasan", "vijay", "dhanush"]
        },
        "president": {
            "incumbent": "Droupadi Murmu",
            "aliases": ["droupadi murmu", "murmu"],
            "disqualified_sports": ["sachin tendulkar", "sachin", "tendulkar", "virat kohli", "ms dhoni"],
            "disqualified_actors": ["suriya", "rajinikanth", "kamal haasan", "vijay"]
        }
    }

    if role in KNOWN_UNION_MINISTERS and jurisdiction == "india":
        minister_info = KNOWN_UNION_MINISTERS[role]
        actual_incumbent = minister_info["incumbent"]
        
        is_disqualified_sports = any(s in subj or subj in s for s in minister_info.get("disqualified_sports", []))
        is_disqualified_actor = any(a in subj or subj in a for a in minister_info.get("disqualified_actors", []))
        
        all_text = " ".join([f"{a.get('title','')} {a.get('content','')}".lower() for a in evidence_articles])
        has_actual_incumbent = any(al in all_text for al in minister_info["aliases"])
        has_sports_bio = any(kw in all_text for kw in ["cricketer", "batsman", "cricket", "test match", "odi", "sports"])
        
        if is_disqualified_sports or is_disqualified_actor or (has_sports_bio and not has_actual_incumbent):
            category = "sports icon / cricketer" if (is_disqualified_sports or has_sports_bio) else "actor / film personality"
            reason = (
                f"Factual Role Contradiction: Evidence confirms {subj_display} is a {category} and does not "
                f"hold the public office of {role.title()} of India (held by {actual_incumbent})."
            )
            processed = []
            for art in evidence_articles:
                art_copy = dict(art)
                art_text = f"{art.get('title','')} {art.get('content','')}".lower()
                if any(al in art_text for al in minister_info["aliases"]):
                    art_copy['stance'] = 'CONTRADICTS'
                    art_copy['entity_role_status'] = f"Refuting: Identifies actual officeholder as {actual_incumbent}"
                    art_copy['relevance_score'] = 0.90
                elif any(kw in art_text for kw in ["cricketer", "cricket", "batsman", "actor", "sports"]):
                    art_copy['stance'] = 'CONTRADICTS'
                    art_copy['entity_role_status'] = f"Refuting: Confirms {subj_display} is a {category} with no cabinet portfolio"
                    art_copy['relevance_score'] = 0.85
                else:
                    art_copy['stance'] = 'NEUTRAL'
                    art_copy['entity_role_status'] = "Neutral Background"
                    art_copy['relevance_score'] = min(art_copy.get('relevance_score', 0.5), 0.25)
                processed.append(art_copy)
                
            return {
                "is_contradiction_detected": True,
                "contradiction_reason": reason,
                "is_supported_detected": False,
                "support_reason": "",
                "supporting_articles_count": 0,
                "contradicting_articles_count": max(1, len([a for a in processed if a.get('stance') == 'CONTRADICTS'])),
                "processed_articles": processed
            }

    return base_res


def patch_evaluate_article_stance(claim: str, art: dict, content_keywords: list) -> str:
    """
    Evaluates 3-way stance (SUPPORTS, CONTRADICTS, NEUTRAL) for a single article.
    Strictly avoids false SUPPORTS votes from loose keyword co-occurrence.
    """
    status = art.get("entity_role_status", "")
    if "Refuting" in status or "Contradiction" in status or "Cross-Domain" in status or "Hoax" in status:
        return "CONTRADICTS"
    if "Direct Support" in status or "Supporting" in status:
        return "SUPPORTS"

    title_lower = art.get('title', '').lower()
    content_lower = art.get('content', '').lower()
    text = f"{title_lower} {content_lower}"

    refute_markers = [
        "fake", "hoax", "false", "misleading", "debunked", "untrue", "myth",
        "denies", "clarifies", "baseless", "fabricated", "not true", "rumour", "rumor",
        "no such", "disproved", "fact check: false", "fact check:", "pib fact check"
    ]
    if any(rm in text for rm in refute_markers):
        return "CONTRADICTS"

    spo = patch_extract_claim_spo(claim)
    if spo.get("is_role_claim"):
        subj = spo["subject"]
        role = spo["role"]
        role_kw = "chief minister" if role == "cm" else ("prime minister" if role == "pm" else role)
        pred_patterns = [
            rf'\b{re.escape(role_kw)}\s+(?:of\s+[a-z\s]+\s+)?{re.escape(subj)}\b',
            rf'\b{re.escape(subj)}\s+(?:was\s+)?(?:sworn in as|elected as|becomes|is|appointed as)\s+(?:the\s+)?{re.escape(role_kw)}\b'
        ]
        if any(re.search(p, text) for p in pred_patterns):
            return "SUPPORTS"
        else:
            return "NEUTRAL"

    rel = art.get("relevance_score", 0.0)
    matched_kw_count = sum(1 for kw in content_keywords if kw in text)
    total_kw = max(1, len(content_keywords))
    overlap = matched_kw_count / float(total_kw)

    if rel >= 0.70 and overlap >= 0.60:
        return "SUPPORTS"
    elif any(rm in text for rm in refute_markers):
        return "CONTRADICTS"
    else:
        return "NEUTRAL"

