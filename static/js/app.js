// Global state storing current verification result
let g_verificationData = null;
let g_currentThreshold = 0.50;

document.addEventListener("DOMContentLoaded", () => {
    console.log("The Fake News AI Platform 6-Module Unified App initialized.");
});

function scrollToInput() {
    const inputSection = document.getElementById("claim-input-section");
    if (inputSection) {
        inputSection.scrollIntoView({ behavior: "smooth" });
    }
}

function loadSampleText(text) {
    const input = document.getElementById("claim-input");
    if (input) {
        input.value = text;
        scrollToInput();
        runVerification();
    }
}

function loadSample(buttonElement) {
    const claimText = buttonElement.innerText;
    document.getElementById("claim-input").value = claimText;
    runVerification();
}

// -------------------------------------------------------------
// Single-Page View Router Engine (All 8 Views: Dashboard, Mod 1-6, Summary)
// -------------------------------------------------------------
function switchPage(pageId) {
    const pages = ["dashboard", "mod1", "mod2", "mod3", "mod4", "mod5", "mod6", "summary"];
    pages.forEach(p => {
        const pageEl = document.getElementById(`page-${p}`);
        const btnEl = document.getElementById(`nav-btn-${p}`);
        if (pageEl) pageEl.classList.add("hidden");
        if (btnEl) btnEl.classList.remove("active");
    });

    const targetPage = document.getElementById(`page-${pageId}`);
    const targetBtn = document.getElementById(`nav-btn-${pageId}`);
    if (targetPage) targetPage.classList.remove("hidden");
    if (targetBtn) targetBtn.classList.add("active");

    // Re-render canvas diagram if switching to Module 3
    if (pageId === "mod3" && g_verificationData) {
        setTimeout(() => {
            renderModule3Page(g_verificationData.module3_independence);
        }, 50);
    }
}

async function runVerification() {
    const claimInput = document.getElementById("claim-input");
    const claimText = claimInput.value.trim();

    if (!claimText) {
        showError("Please enter a news claim or select one of the benchmark samples.");
        return;
    }

    hideError();
    showLoader();
    hideResults();

    try {
        const response = await fetch("/api/verify", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ claim: claimText })
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.error || "Verification pipeline execution failed.");
        }

        const data = await response.json();
        g_verificationData = data;
        renderAllPages(data);
        switchPage("dashboard");

        // Trigger MathJax re-render for formulas
        if (window.MathJax && window.MathJax.typesetPromise) {
            window.MathJax.typesetPromise();
        }

    } catch (err) {
        showError(err.message || "An unexpected error occurred during claim verification.");
    } finally {
        hideLoader();
    }
}

function renderAllPages(data) {
    // 1. Overview Dashboard Page
    renderOverviewDashboard(data);

    // 2. Dedicated Module 1 Page (RoBERTa)
    renderModule1Page(data.module1_detection);

    // 3. Dedicated Module 2 Page (Live Evidence)
    renderModule2Page(data.module2_retrieval);

    // 4. Dedicated Module 3 Page (Source Clustering & Independence)
    renderModule3Page(data.module3_independence);

    // 5. Dedicated Module 4 Page (Agentic Verification)
    renderModule4Page(data.module4_agentic);

    // 6. Dedicated Module 5 Page (Source Credibility Assessment)
    renderModule5Page(data.module5_credibility);

    // 7. Dedicated Module 6 Page (Trust Score Fusion Engine)
    renderModule6Page(data.module6_fusion, data);

    // 8. Verification Audit Summary Page
    renderSummaryPage(data);

    // Show Results Dashboard
    const resEl = document.getElementById("results-dashboard");
    if (resEl) resEl.classList.remove("hidden");
}

// -------------------------------------------------------------
// 1. Render Overview Dashboard Page
// -------------------------------------------------------------
function renderOverviewDashboard(data) {
    document.getElementById("result-claim-title").innerText = `"${data.claim}"`;

    const verdictBadge = document.getElementById("final-verdict-badge");
    verdictBadge.innerText = data.final_verdict.toUpperCase();
    verdictBadge.className = `verdict-badge badge-${data.final_verdict.toLowerCase()}`;

    const trustBadge = document.getElementById("trust-score-badge");
    trustBadge.innerHTML = `<i class="fa-solid fa-shield"></i> Trust Score: ${data.preliminary_trust_score}%`;
    trustBadge.className = `trust-pill pill-${data.final_verdict.toLowerCase()}`;

    document.getElementById("execution-time-badge").innerHTML = `<i class="fa-solid fa-clock"></i> ${data.execution_time_seconds}s`;

    // 5-Module Score Equation Bar
    const scores = data.module_confidence_scores;
    document.getElementById("eq-c1").innerText = `${Math.round(scores.module1_content_confidence * 100)}%`;
    document.getElementById("eq-c2").innerText = `${Math.round(scores.module2_evidence_confidence * 100)}%`;
    document.getElementById("eq-c3").innerText = `${(scores.module3_independence_confidence * 100).toFixed(1)}%`;
    document.getElementById("eq-c4").innerText = `${Math.round(scores.module4_agentic_confidence * 100)}%`;
    document.getElementById("eq-c5").innerText = `${Math.round(scores.module5_credibility_confidence * 100)}%`;
    document.getElementById("eq-trust").innerText = `${data.preliminary_trust_score}%`;

    // Module 1 Card
    const mod1 = data.module1_detection;
    const dashC1Pred = document.getElementById("dash-c1-pred");
    dashC1Pred.innerText = mod1.label.toUpperCase();
    dashC1Pred.className = `pred-text text-${mod1.label.toLowerCase()}`;
    document.getElementById("dash-c1-score").innerText = `${Math.round(mod1.confidence_score * 100)}%`;

    // Module 2 Card
    const mod2 = data.module2_retrieval;
    document.getElementById("dash-evidence-count").innerText = `${mod2.total_articles_retrieved} Articles`;
    document.getElementById("dash-c2-score").innerText = `${Math.round(mod2.evidence_support_score * 100)}%`;
    document.getElementById("dash-c2-status").innerText = mod2.evidence_status;

    // Module 3 Card
    const mod3 = data.module3_independence;
    document.getElementById("dash-c3-score").innerText = mod3.source_independence_score.toFixed(2);
    document.getElementById("dash-c3-status").innerText = `${mod3.independent_sources_count} unique origins out of ${mod3.total_articles_analyzed} articles`;

    // Module 4 Card (Agentic)
    const mod4 = data.module4_agentic;
    const dashC4Verdict = document.getElementById("dash-c4-verdict");
    dashC4Verdict.innerText = mod4.agent_verdict.toUpperCase();
    dashC4Verdict.className = `pred-text text-${mod4.agent_verdict.toLowerCase()}`;
    document.getElementById("dash-c4-score").innerText = `${Math.round(mod4.agent_confidence_score * 100)}%`;
    document.getElementById("dash-c4-status").innerText = `${mod4.tools_invoked_count} tools autonomously executed`;

    // Module 5 Card (Credibility)
    const mod5 = data.module5_credibility;
    document.getElementById("dash-c5-score").innerText = mod5.source_credibility_score.toFixed(2);
    document.getElementById("dash-c5-status").innerText = `${mod5.tier_percentages.tier1_pct}% Tier 1 (Wire/Authoritative)`;

    // Module 6 Card (Fusion)
    const mod6 = data.module6_fusion;
    const dashFusionVerdict = document.getElementById("dash-fusion-verdict");
    dashFusionVerdict.innerText = mod6.final_verdict.toUpperCase();
    dashFusionVerdict.className = `pred-text text-${mod6.final_verdict.toLowerCase()}`;
    document.getElementById("dash-fusion-score").innerText = `${mod6.final_trust_score}%`;
    document.getElementById("dash-fusion-status").innerText = mod6.is_contradiction_active ? "Contradiction Gate: ACTIVE" : "Calibrated Ensemble";
}

// -------------------------------------------------------------
// 2. Render Module 1 Dedicated View (RoBERTa)
// -------------------------------------------------------------
function renderModule1Page(mod1) {
    const labelEl = document.getElementById("full-mod1-label");
    labelEl.innerText = mod1.label.toUpperCase();
    labelEl.className = `pred-highlight text-${mod1.label.toLowerCase()}`;
    document.getElementById("full-mod1-conf").innerText = `${Math.round(mod1.confidence_score * 100)}%`;

    const probs = mod1.probabilities;
    const realPct = Math.round(probs.Real * 100);
    const fakePct = Math.round(probs.Fake * 100);
    const unverPct = Math.round(probs.Unverified * 100);

    document.getElementById("prob-real-val").innerText = `${realPct}%`;
    document.getElementById("prob-real-bar").style.width = `${realPct}%`;

    document.getElementById("prob-fake-val").innerText = `${fakePct}%`;
    document.getElementById("prob-fake-bar").style.width = `${fakePct}%`;

    document.getElementById("prob-unverified-val").innerText = `${unverPct}%`;
    document.getElementById("prob-unverified-bar").style.width = `${unverPct}%`;
}

// -------------------------------------------------------------
// 3. Render Module 2 Dedicated View (Live Evidence)
// -------------------------------------------------------------
function renderModule2Page(mod2) {
    document.getElementById("full-c2-score").innerText = `${Math.round(mod2.evidence_support_score * 100)}%`;
    document.getElementById("full-evidence-status-badge").innerText = mod2.evidence_status;

    const backendsEl = document.getElementById("full-backends-list");
    backendsEl.innerHTML = (mod2.backends_used || []).map(b => `<span class="backend-tag"><i class="fa-solid fa-check text-emerald"></i> ${b}</span>`).join("");

    document.getElementById("full-articles-count").innerText = mod2.total_articles_retrieved;
    const articlesFeedEl = document.getElementById("full-articles-list");
    articlesFeedEl.innerHTML = (mod2.evidence_items || []).map((art, idx) => {
        const relPct = Math.round((art.relevance_score || 0) * 100);
        const simPct = art.claim_similarity != null ? Math.round(art.claim_similarity * 100) : null;
        const relColor = relPct >= 60 ? '#00845a' : relPct >= 30 ? '#e67e22' : '#c0392b';
        const statusText = art.date_match_status || art.entity_role_status || '';
        const isCrossDomain = statusText.toLowerCase().includes('cross-domain') || statusText.toLowerCase().includes('contradiction');
        return `
        <div class="article-item-card" style="border-left: 3px solid ${relColor};">
            <div class="art-title">${idx + 1}. <a href="${art.url || '#'}" target="_blank" style="color: inherit; text-decoration: none;">${escapeHtml(art.title)} <i class="fa-solid fa-arrow-up-right-from-square" style="font-size: 0.75rem; color: #00845a; margin-left: 4px;"></i></a></div>
            <div class="art-meta">
                <span class="art-domain"><i class="fa-solid fa-globe"></i> ${escapeHtml(art.domain)}</span>
                <span class="art-method">${escapeHtml(art.source)}</span>
                <span style="color:${relColor}; font-weight:600;">Relevance: ${relPct}%</span>
                ${simPct != null ? `<span style="color:#888; font-size:0.78rem;">Claim-Match: ${simPct}%</span>` : ''}
            </div>
            ${isCrossDomain ? `<div style="font-size:0.76rem; color:#c0392b; margin-top:5px; font-weight:600;"><i class="fa-solid fa-triangle-exclamation"></i> ${escapeHtml(statusText)}</div>` : (statusText ? `<div style="font-size:0.75rem; color:#00845a; margin-top:4px;"><i class="fa-solid fa-clock"></i> ${escapeHtml(statusText)}</div>` : '')}
        </div>
    `}).join("");
}

// -------------------------------------------------------------
// 4. Render Module 3 Dedicated View (Clustering)
// -------------------------------------------------------------
function renderModule3Page(mod3) {
    document.getElementById("full-mod3-score").innerText = `${Math.round(mod3.source_independence_score * 100)}%`;
    document.getElementById("full-independent-count").innerText = mod3.independent_sources_count;
    document.getElementById("full-duplication-rate").innerText = `${mod3.duplication_rate_percent}%`;

    const clustersFeedEl = document.getElementById("full-clusters-feed");
    clustersFeedEl.innerHTML = (mod3.clusters || []).map(cls => `
        <div class="cluster-card">
            <div class="cluster-head">
                <span class="cluster-id"><i class="fa-solid fa-folder text-emerald"></i> Story Cluster #${cls.cluster_id + 1}</span>
                <span class="${cls.is_syndicated ? 'syndicated-badge' : 'unique-badge'}">
                    ${cls.is_syndicated ? `<i class="fa-solid fa-copy"></i> Syndicated (${cls.article_count} outlets)` : `<i class="fa-solid fa-certificate"></i> Independent`}
                </span>
            </div>
            <div class="cluster-title">${escapeHtml(cls.primary_headline)}</div>
            <div class="cluster-outlets"><i class="fa-solid fa-newspaper"></i> Outlets: ${cls.domains_involved.join(", ")}</div>
        </div>
    `).join("");

    renderBubbleClusterDiagram(mod3.nodes || [], mod3.edges || [], mod3.clusters || [], g_currentThreshold);
}

function updateSimilarityThreshold(val) {
    g_currentThreshold = parseFloat(val);
    document.getElementById("slider-val-display").innerText = g_currentThreshold.toFixed(2);
    if (g_verificationData && g_verificationData.module3_independence) {
        renderBubbleClusterDiagram(
            g_verificationData.module3_independence.nodes || [],
            g_verificationData.module3_independence.edges || [],
            g_verificationData.module3_independence.clusters || [],
            g_currentThreshold
        );
    }
}

// -------------------------------------------------------------
// 5. Render Module 4 Dedicated View (Agentic Verification)
// -------------------------------------------------------------
function renderModule4Page(mod4) {
    const verdictEl = document.getElementById("full-mod4-verdict");
    verdictEl.innerText = mod4.agent_verdict.toUpperCase();
    verdictEl.className = `metric-val text-${mod4.agent_verdict.toLowerCase()}`;
    document.getElementById("full-mod4-score").innerText = `${Math.round(mod4.agent_confidence_score * 100)}%`;
    document.getElementById("full-mod4-tools-count").innerText = `${mod4.tools_invoked_count} Tools`;

    // Tools list
    const toolsListEl = document.getElementById("full-mod4-tools-list");
    toolsListEl.innerHTML = (mod4.tools_invoked || []).map(t => `<span class="backend-tag"><i class="fa-solid fa-wrench text-emerald"></i> ${escapeHtml(t)}</span>`).join("");

    // Reasoning Trace
    const traceEl = document.getElementById("full-mod4-reasoning-trace");
    traceEl.innerHTML = (mod4.reasoning_trace || []).map((step, idx) => `
        <div class="reasoning-step-item">
            <div class="step-head">
                <span class="step-badge">Step ${idx + 1}</span>
                <span class="step-phase">${escapeHtml(step.phase)}</span>
            </div>
            <div class="step-thought">${escapeHtml(step.thought)}</div>
        </div>
    `).join("");

    // Explainable Report Markdown View
    const reportEl = document.getElementById("full-mod4-report-content");
    const rep = mod4.explainable_report || {};
    reportEl.innerHTML = `
        <div class="report-executive-box">
            <div class="rep-badge-row">
                <span class="verdict-badge badge-${(mod4.agent_verdict || 'unverified').toLowerCase()}">${escapeHtml(rep.verdict_badge || mod4.agent_verdict)}</span>
                <span class="time-pill">Agent Confidence: <strong>${rep.confidence_percent || Math.round(mod4.agent_confidence_score * 100)}%</strong></span>
            </div>
            <p style="margin-top: 10px; font-weight: 500; color: #1a1a1a;">${escapeHtml(rep.executive_summary || '')}</p>
        </div>
        <div style="margin-top: 16px;">
            <h4 style="margin-bottom: 8px;"><i class="fa-solid fa-clipboard-check text-emerald"></i> Core Investigation Findings:</h4>
            <ul style="padding-left: 20px; line-height: 1.6; color: #333;">
                ${(rep.findings_list || []).map(f => `<li>${escapeHtml(f.replace(/\*\*/g, ''))}</li>`).join("")}
            </ul>
        </div>
    `;
}

// -------------------------------------------------------------
// 6. Render Module 5 Dedicated View (Source Credibility)
// -------------------------------------------------------------
function renderModule5Page(mod5) {
    document.getElementById("full-mod5-score").innerText = `${Math.round(mod5.source_credibility_score * 100)}%`;
    document.getElementById("full-tier1-pct").innerText = `${mod5.tier_percentages.tier1_pct}%`;
    document.getElementById("full-tier2-pct").innerText = `${mod5.tier_percentages.tier2_pct}%`;

    const sourcesGridEl = document.getElementById("full-sources-credibility-grid");
    sourcesGridEl.innerHTML = (mod5.evaluated_sources || []).map(s => {
        const scorePct = Math.round(s.credibility_score * 100);
        const tierColor = s.tier.includes("Tier 1") ? "#00845a" : (s.tier.includes("Tier 2") ? "#0284c7" : "#e67e22");
        return `
        <div class="credibility-source-card" style="border-top: 3px solid ${tierColor};">
            <div class="source-card-head">
                <strong><a href="${s.url}" target="_blank" style="color: inherit; text-decoration: none;">${escapeHtml(s.publisher_name)}</a></strong>
                <span class="tier-badge" style="background: ${tierColor}15; color: ${tierColor};">${escapeHtml(s.tier.split(':')[0])}</span>
            </div>
            <div class="source-domain"><i class="fa-solid fa-globe"></i> ${escapeHtml(s.domain)}</div>
            <div class="source-metrics-row">
                <span>Trust Score: <strong style="color:${tierColor}">${scorePct}%</strong></span>
                <span>Factuality: <strong>${escapeHtml(s.factuality)}</strong></span>
            </div>
            <p class="source-desc">${escapeHtml(s.description)}</p>
        </div>
    `}).join("");
}

// -------------------------------------------------------------
// 7. Render Module 6 Dedicated View (Trust Score Fusion)
// -------------------------------------------------------------
function renderModule6Page(mod6, fullData) {
    document.getElementById("full-mod6-score").innerText = `${mod6.final_trust_score}%`;
    const verdictEl = document.getElementById("full-mod6-verdict");
    verdictEl.innerText = mod6.final_verdict.toUpperCase();
    verdictEl.className = `metric-val text-${mod6.final_verdict.toLowerCase()}`;

    const fb = mod6.formula_breakdown || {};
    document.getElementById("full-mod6-logit").innerText = fb.logistic_logit_z != null ? fb.logistic_logit_z : "0.00";

    // Terms Table
    const tableEl = document.getElementById("fusion-terms-table");
    tableEl.innerHTML = `
        <table class="terms-table">
            <thead>
                <tr>
                    <th>Module Dimension</th>
                    <th>Weight (\(w_i\))</th>
                    <th>Confidence (\(C_i\))</th>
                    <th>Weighted Term (\(w_i \cdot C_i\))</th>
                </tr>
            </thead>
            <tbody>
                ${(fb.terms || []).map(t => `
                    <tr>
                        <td><strong>${escapeHtml(t.module)}</strong></td>
                        <td>${t.weight}</td>
                        <td>${Math.round(t.confidence * 100)}%</td>
                        <td><strong>${(t.weighted_value * 100).toFixed(2)}%</strong></td>
                    </tr>
                `).join("")}
                <tr class="table-total-row">
                    <td><strong>Linear Weighted Sum</strong></td>
                    <td><strong>1.00</strong></td>
                    <td>—</td>
                    <td><strong class="text-emerald">${fb.linear_weighted_sum}%</strong></td>
                </tr>
            </tbody>
        </table>
    `;

    document.getElementById("fusion-decision-rationale").innerText = mod6.verdict_rationale;
}

// -------------------------------------------------------------
// 8. Render Verification Audit Summary Page
// -------------------------------------------------------------
function renderSummaryPage(data) {
    document.getElementById("report-claim").innerText = `"${data.claim}"`;

    const verdictEl = document.getElementById("report-verdict-badge");
    verdictEl.innerText = data.final_verdict.toUpperCase();
    verdictEl.className = `verdict-badge badge-${data.final_verdict.toLowerCase()}`;

    document.getElementById("report-trust-val").innerText = `${data.preliminary_trust_score}%`;

    const scores = data.module_confidence_scores;
    document.getElementById("report-c1-val").innerText = `${Math.round(scores.module1_content_confidence * 100)}%`;
    document.getElementById("report-c2-val").innerText = `${Math.round(scores.module2_evidence_confidence * 100)}%`;
    document.getElementById("report-c3-val").innerText = `${Math.round(scores.module3_independence_confidence * 100)}%`;
    document.getElementById("report-c4-val").innerText = `${Math.round(scores.module4_agentic_confidence * 100)}%`;
    document.getElementById("report-c5-val").innerText = `${Math.round(scores.module5_credibility_confidence * 100)}%`;
}

// -------------------------------------------------------------
// Force-Directed Bubble Cluster Diagram Engine (Canvas)
// -------------------------------------------------------------
function renderBubbleClusterDiagram(nodes, edges, clusters, threshold) {
    const canvas = document.getElementById("bubble-cluster-canvas");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");

    const width = canvas.width;
    const height = canvas.height;
    ctx.clearRect(0, 0, width, height);

    if (!nodes || nodes.length === 0) {
        ctx.fillStyle = "#555555";
        ctx.font = "16px Inter";
        ctx.textAlign = "center";
        ctx.fillText("No cluster graph data available", width / 2, height / 2);
        return;
    }

    const clusterColors = [
        "#0284c7", "#7c3aed", "#00845a", "#e11d48", "#d97706", "#2563eb", "#db2777"
    ];

    const clusterMap = {};
    clusters.forEach((c, idx) => {
        clusterMap[c.cluster_id] = {
            color: clusterColors[idx % clusterColors.length],
            is_syndicated: c.is_syndicated,
            count: c.article_count,
            primary_headline: c.primary_headline
        };
    });

    const clusterHubs = {};
    const clusterIds = Object.keys(clusterMap);
    const numClusters = clusterIds.length;
    const centerX = width / 2;
    const centerY = height / 2;
    const radiusX = width * 0.36;
    const radiusY = height * 0.33;

    clusterIds.forEach((cid, i) => {
        const angle = (i / Math.max(1, numClusters)) * 2 * Math.PI - Math.PI / 2;
        clusterHubs[cid] = {
            x: centerX + radiusX * Math.cos(angle),
            y: centerY + radiusY * Math.sin(angle)
        };
    });

    const nodePositions = [];
    const clusterCounters = {};

    nodes.forEach((n, idx) => {
        const cid = n.cluster_id;
        const hub = clusterHubs[cid] || { x: centerX, y: centerY };
        clusterCounters[cid] = (clusterCounters[cid] || 0) + 1;
        const countInCluster = clusterCounters[cid];

        let x, y;
        if (clusterMap[cid] && clusterMap[cid].is_syndicated) {
            const subAngle = countInCluster * 1.35;
            const subRad = 32 + (countInCluster * 6);
            x = hub.x + subRad * Math.cos(subAngle);
            y = hub.y + subRad * Math.sin(subAngle);
        } else {
            const randomOffset = (idx * 43) % 24 - 12;
            x = hub.x + randomOffset;
            y = hub.y + randomOffset;
        }

        x = Math.max(45, Math.min(width - 45, x));
        y = Math.max(45, Math.min(height - 45, y));

        nodePositions.push({
            ...n,
            x: x,
            y: y,
            radius: 10,
            color: clusterMap[cid] ? clusterMap[cid].color : "#0284c7"
        });
    });

    // Draw Syndicated Cluster Outline Bubbles
    clusterIds.forEach(cid => {
        const cInfo = clusterMap[cid];
        if (cInfo && cInfo.is_syndicated) {
            const hub = clusterHubs[cid];
            ctx.beginPath();
            ctx.arc(hub.x, hub.y, 65, 0, 2 * Math.PI);
            ctx.fillStyle = `${cInfo.color}10`;
            ctx.fill();
            ctx.strokeStyle = `${cInfo.color}50`;
            ctx.lineWidth = 1.5;
            ctx.setLineDash([4, 4]);
            ctx.stroke();
            ctx.setLineDash([]);
        }
    });

    // Draw Edges
    edges.forEach(e => {
        if (e.similarity >= threshold && e.source < nodePositions.length && e.target < nodePositions.length) {
            const n1 = nodePositions[e.source];
            const n2 = nodePositions[e.target];
            ctx.beginPath();
            ctx.moveTo(n1.x, n1.y);
            ctx.lineTo(n2.x, n2.y);
            ctx.strokeStyle = "rgba(0, 132, 90, 0.45)";
            ctx.lineWidth = Math.max(1, e.similarity * 2.5);
            ctx.stroke();
        }
    });

    // Draw Nodes
    nodePositions.forEach(n => {
        ctx.beginPath();
        ctx.arc(n.x, n.y, n.radius, 0, 2 * Math.PI);
        ctx.fillStyle = n.color;
        ctx.fill();
        ctx.strokeStyle = "#ffffff";
        ctx.lineWidth = 2;
        ctx.stroke();

        // Label
        ctx.fillStyle = "#222222";
        ctx.font = "11px Inter";
        ctx.textAlign = "center";
        ctx.fillText(n.label.substring(0, 14), n.x, n.y + n.radius + 13);
    });
}

function showLoader() {
    const el = document.getElementById("loader-section");
    if (el) el.classList.remove("hidden");
}

function hideLoader() {
    const el = document.getElementById("loader-section");
    if (el) el.classList.add("hidden");
}

function hideResults() {
    const el = document.getElementById("results-dashboard");
    if (el) el.classList.add("hidden");
}

function showError(msg) {
    const el = document.getElementById("error-box");
    if (el) {
        el.innerText = msg;
        el.classList.remove("hidden");
    }
}

function hideError() {
    const el = document.getElementById("error-box");
    if (el) el.classList.add("hidden");
}

function escapeHtml(text) {
    if (!text) return "";
    return text.toString()
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

async function downloadVerificationReport() {
    if (!g_verificationData) {
        showError("Please verify a claim first before downloading the report.");
        return;
    }

    const claimText = g_verificationData.claim || "";
    const bannerBtn = document.getElementById("download-report-btn-banner");
    const summaryBtn = document.getElementById("download-report-btn-summary");
    
    const originalBannerText = bannerBtn ? bannerBtn.innerHTML : "";
    const originalSummaryText = summaryBtn ? summaryBtn.innerHTML : "";
    
    if (bannerBtn) bannerBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Preparing PDF...';
    if (summaryBtn) summaryBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Preparing PDF...';

    try {
        const response = await fetch("/api/download_report", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                claim: claimText,
                verification_data: g_verificationData
            })
        });

        if (!response.ok) {
            throw new Error("Failed to generate PDF report.");
        }

        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.style.display = "none";
        a.href = downloadUrl;
        
        const cleanName = claimText.substring(0, 25).replace(/[^a-zA-Z0-9]/g, "_") || "Fact_Check";
        a.download = `Fact_Check_Report_${cleanName}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(downloadUrl);
        document.body.removeChild(a);

    } catch (err) {
        showError(err.message || "Could not download verification report.");
    } finally {
        if (bannerBtn) bannerBtn.innerHTML = originalBannerText;
        if (summaryBtn) summaryBtn.innerHTML = originalSummaryText;
    }
}
