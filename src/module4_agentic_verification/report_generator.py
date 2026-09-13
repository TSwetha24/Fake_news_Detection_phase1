from typing import Dict, Any, List

def generate_explainable_report(
    claim: str,
    verdict: str,
    confidence: float,
    reasoning_trace: List[Dict[str, Any]],
    tool_results: Dict[str, Any],
    evidence_articles: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Generates a structured, highly neat, human-readable fact-checking verification report
    with executive summary, biomedical consensus, evidence analysis, tool audit trail, and verdict justification.
    """
    verdict_badge = "🟢 VERIFIED REAL" if verdict == "Real" else ("🔴 CONFIRMED FAKE" if verdict == "Fake" else "🟡 UNVERIFIED / DISPUTED")
    confidence_pct = round(confidence * 100, 1)

    findings = []
    
    # 1. Check Medical / Scientific Fact Findings
    med_tool = tool_results.get("medical_scientific_fact_checker", {})
    if med_tool.get("scientific_fact_check_active"):
        findings.append(f"🔬 **Scientific & Medical Consensus**: {med_tool.get('medical_consensus')} *(Source: {med_tool.get('authority')})*")

    # 2. Check Authority Attribution Audit Findings
    auth_tool = tool_results.get("authority_attribution_checker", {})
    if auth_tool.get("vague_authority_detected"):
        findings.append(f"🚩 **Unverified Authority Attribution**: Headline uses '{auth_tool.get('flagged_phrase')}' — {auth_tool.get('audit_note')}")

    # 3. Check Cross-Domain Findings
    cross_tool = tool_results.get("cross_domain_auditor", {})
    if cross_tool.get("domain_mismatch_detected"):
        findings.append(f"⚠️ **Institutional Authority Mismatch**: {cross_tool.get('reasoning')}")
        
    # 4. Check Temporal Recency Findings
    temporal_tool = tool_results.get("temporal_recency_checker", {})
    if temporal_tool.get("temporal_conflict_detected"):
        findings.append(f"⏱️ **Temporal Inconsistency**: {temporal_tool.get('details')}")

    # 5. Check Entity Facts
    entity_tool = tool_results.get("entity_fact_lookup", {})
    for ent in entity_tool.get("entities_found", []):
        findings.append(f"👤 **Entity Profile**: {ent['entity']} is recognized as *{ent['known_role']}* ({ent['status']}).")

    # 6. Check Stance
    stance_tool = tool_results.get("stance_entailment_analyzer", {})
    findings.append(f"📊 **Evidence Stance Breakdown**: {stance_tool.get('supporting_articles', 0)} supporting, {stance_tool.get('refuting_articles', 0)} refuting, {stance_tool.get('neutral_articles', 0)} neutral articles analyzed.")

    if not findings:
        findings.append("Evidence retrieved matches standard factual reporting norms.")

    findings_md = "\n".join([f"- {f}" for f in findings])

    # Construct the report Markdown
    report_markdown = f"""### TRUTHCHAIN AI AGENTIC VERIFICATION REPORT

**Claim Under Investigation:** *"{claim}"*  
**Autonomous Agent Verdict:** **{verdict_badge}** (Confidence: **{confidence_pct}%**)

---

#### 1. Core Investigation Findings
{findings_md}

#### 2. Autonomous Agent Reasoning Trace
"""
    for idx, step in enumerate(reasoning_trace, 1):
        report_markdown += f"- **Step {idx} [{step['phase']}]:** {step['thought']}\n"

    report_markdown += f"""
#### 3. Final Analytical Rationale
Based on multi-tool autonomous cross-examination of live news wire archives and institutional knowledge bases, this claim is categorized as **{verdict.upper()}**.
"""

    return {
        "verdict_badge": verdict_badge,
        "confidence_percent": confidence_pct,
        "executive_summary": f"Autonomous verification concluded that the claim is {verdict} with {confidence_pct}% agent confidence.",
        "findings_list": findings,
        "report_markdown": report_markdown.strip()
    }
