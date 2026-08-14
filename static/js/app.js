// Global state storing current verification result
let g_verificationData = null;
let g_currentThreshold = 0.75;

document.addEventListener("DOMContentLoaded", () => {
    console.log("The Fake News AI Platform App initialized.");
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
// Single-Page View Router Engine
// -------------------------------------------------------------
function switchPage(pageId) {
    // Hide all pages
    const pages = ["dashboard", "mod1", "mod2", "mod3", "summary"];
    pages.forEach(p => {
        const pageEl = document.getElementById(`page-${p}`);
        const btnEl = document.getElementById(`nav-btn-${p}`);
        if (pageEl) pageEl.classList.add("hidden");
        if (btnEl) btnEl.classList.remove("active");
    });

    // Show target page
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
        showError("Please enter a news claim or select one of the sample claims.");
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
            throw new Error(errData.error || "Verification pipeline failed.");
        }

        const data = await response.json();
        g_verificationData = data;
        renderAllPages(data);
        switchPage("dashboard");

    } catch (err) {
        showError(err.message || "An unexpected network or server error occurred.");
    } finally {
        hideLoader();
    }
}

function renderAllPages(data) {
    // 1. Overview Dashboard Page
    renderOverviewDashboard(data);

    // 2. Module 1 Dedicated Page
    renderModule1Page(data.module1_detection);

    // 3. Module 2 Dedicated Page
    renderModule2Page(data.module2_retrieval);

    // 4. Module 3 Dedicated Page & Bubble Visualizer
    renderModule3Page(data.module3_independence);

    // 5. Synthesis Report Page
    renderSummaryReport(data);

    showResults();
}

// -------------------------------------------------------------
// 1. Render Overview Dashboard
// -------------------------------------------------------------
function renderOverviewDashboard(data) {
    document.getElementById("result-claim-title").innerText = `"${data.claim}"`;
    document.getElementById("trust-score-badge").innerHTML = `<i class="fa-solid fa-shield"></i> Trust Score: ${data.preliminary_trust_score}%`;
    document.getElementById("execution-time-badge").innerHTML = `<i class="fa-solid fa-clock"></i> ${data.execution_time_seconds}s`;

    // Final Verdict Badge
    const finalVerdict = data.final_verdict;
    const finalBadgeEl = document.getElementById("final-verdict-badge");
    finalBadgeEl.className = "verdict-badge";
    if (finalVerdict === "Real") {
        finalBadgeEl.classList.add("badge-real");
        finalBadgeEl.innerHTML = `<i class="fa-solid fa-circle-check"></i> REAL`;
    } else if (finalVerdict === "Fake") {
        finalBadgeEl.classList.add("badge-fake");
        finalBadgeEl.innerHTML = `<i class="fa-solid fa-circle-xmark"></i> FAKE`;
    } else {
        finalBadgeEl.classList.add("badge-unverified");
        finalBadgeEl.innerHTML = `<i class="fa-solid fa-circle-exclamation"></i> UNVERIFIED`;
    }

    // 3-Module Fusion Formula Bar
    const scores = data.module_confidence_scores || {};
    const c1Pct = Math.round((scores.module1_content_confidence || 0.7) * 100);
    const c2Pct = Math.round((scores.module2_evidence_confidence || 0.8) * 100);
    const c3Pct = Math.round((scores.module3_independence_confidence || 0.9) * 100);

    document.getElementById("score-c1").innerText = `${c1Pct}%`;
    document.getElementById("score-c2").innerText = `${c2Pct}%`;
    document.getElementById("score-c3").innerText = `${c3Pct}%`;
    document.getElementById("score-final").innerText = `${data.preliminary_trust_score}%`;

    // Overview Cards
    const mod1Badge = document.getElementById("dash-mod1-badge");
    mod1Badge.className = "verdict-badge";
    const mod1Label = data.module1_detection.label;
    if (mod1Label === "Real") {
        mod1Badge.classList.add("badge-real");
        mod1Badge.innerText = "REAL";
    } else if (mod1Label === "Fake") {
        mod1Badge.classList.add("badge-fake");
        mod1Badge.innerText = "FAKE";
    } else {
        mod1Badge.classList.add("badge-unverified");
        mod1Badge.innerText = "UNVERIFIED";
    }

    document.getElementById("dash-mod1-conf").innerText = `${Math.round(data.module1_detection.confidence_score * 100)}%`;
    document.getElementById("dash-mod2-score").innerText = `${c2Pct}%`;
    document.getElementById("dash-mod2-status").innerText = data.module2_retrieval.evidence_status || "Live evidence verification complete";
    document.getElementById("dash-mod3-score").innerText = `${data.module3_independence.source_independence_score}`;
}

// -------------------------------------------------------------
// 2. Render Module 1 Dedicated View
// -------------------------------------------------------------
function renderModule1Page(mod1) {
    const label = mod1.label;
    const confPct = Math.round(mod1.confidence_score * 100);

    const badgeEl = document.getElementById("full-mod1-badge");
    badgeEl.className = "verdict-badge";
    if (label === "Real") {
        badgeEl.classList.add("badge-real");
        badgeEl.innerHTML = `<i class="fa-solid fa-circle-check"></i> REAL`;
    } else if (label === "Fake") {
        badgeEl.classList.add("badge-fake");
        badgeEl.innerHTML = `<i class="fa-solid fa-circle-xmark"></i> FAKE`;
    } else {
        badgeEl.classList.add("badge-unverified");
        badgeEl.innerHTML = `<i class="fa-solid fa-circle-exclamation"></i> UNVERIFIED`;
    }

    document.getElementById("full-mod1-conf").innerText = `${confPct}%`;
    document.getElementById("full-mod1-bar").style.width = `${confPct}%`;

    const probs = mod1.probabilities || {};
    const realPct = Math.round((probs.Real || 0) * 100);
    const fakePct = Math.round((probs.Fake || 0) * 100);
    const unverPct = Math.round((probs.Unverified || 0) * 100);

    document.getElementById("full-prob-real").innerText = `${realPct}%`;
    document.getElementById("full-bar-real").style.width = `${realPct}%`;

    document.getElementById("full-prob-fake").innerText = `${fakePct}%`;
    document.getElementById("full-bar-fake").style.width = `${fakePct}%`;

    document.getElementById("full-prob-unverified").innerText = `${unverPct}%`;
    document.getElementById("full-bar-unverified").style.width = `${unverPct}%`;
}

// -------------------------------------------------------------
// 3. Render Module 2 Dedicated View
// -------------------------------------------------------------
function renderModule2Page(mod2) {
    const c2Pct = Math.round((mod2.evidence_support_score || 0.85) * 100);
    document.getElementById("full-mod2-score").innerText = `${c2Pct}%`;
    document.getElementById("full-mod2-status").innerText = mod2.evidence_status || "Live news verification complete";

    const backendsEl = document.getElementById("full-backends-list");
    backendsEl.innerHTML = (mod2.backends_used || []).map(b => `<span class="backend-tag"><i class="fa-solid fa-check text-emerald"></i> ${b}</span>`).join("");

    document.getElementById("full-articles-count").innerText = mod2.total_articles_retrieved;
    const articlesFeedEl = document.getElementById("full-articles-list");
    articlesFeedEl.innerHTML = (mod2.evidence_items || []).map((art, idx) => `
        <div class="article-item-card">
            <div class="art-title">${idx + 1}. ${escapeHtml(art.title)}</div>
            <div class="art-meta">
                <span class="art-domain"><i class="fa-solid fa-globe"></i> ${escapeHtml(art.domain)}</span>
                <span class="art-method">${escapeHtml(art.source)}</span>
                <span>Relevance: ${Math.round((art.relevance_score || 0.85) * 100)}%</span>
            </div>
            ${art.date_match_status ? `<div style="font-size:0.75rem; color:#00845a; margin-top:4px;"><i class="fa-solid fa-clock"></i> ${art.date_match_status}</div>` : ''}
        </div>
    `).join("");
}

// -------------------------------------------------------------
// 4. Render Module 3 Dedicated View & Force-Directed Bubble Cluster Visualizer
// -------------------------------------------------------------
function renderModule3Page(mod3) {
    document.getElementById("full-mod3-score").innerText = `${mod3.source_independence_score.toFixed(4)}`;
    document.getElementById("full-independent-count").innerText = mod3.independent_sources_count;
    document.getElementById("full-duplication-rate").innerText = `${mod3.duplication_rate_percent}%`;

    // Clusters feed
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

    // Render Canvas Force-Directed Bubble Cluster Diagram
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
// Force-Directed Bubble Cluster Diagram Engine (Light Editorial Theme)
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

    // Color Palette for Clusters
    const clusterColors = [
        "#0284c7", // Sky Blue
        "#7c3aed", // Violet
        "#00845a", // Emerald
        "#e11d48", // Rose
        "#d97706", // Amber
        "#2563eb", // Royal Blue
        "#db2777"  // Pink
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

    const filteredEdges = edges.filter(e => e.similarity >= threshold);

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

    // 1. Draw Translucent Cluster Bubble Containers / Orbs around story clusters
    clusterIds.forEach(cid => {
        const hub = clusterHubs[cid];
        const info = clusterMap[cid];
        const isSynd = info ? info.is_syndicated : false;
        const color = info ? info.color : "#0284c7";

        ctx.beginPath();
        const bubbleRad = isSynd ? 65 : 42;
        ctx.arc(hub.x, hub.y, bubbleRad, 0, 2 * Math.PI);
        ctx.fillStyle = color;
        ctx.globalAlpha = 0.07;
        ctx.fill();

        ctx.strokeStyle = color;
        ctx.globalAlpha = 0.35;
        ctx.lineWidth = 1.5;
        ctx.setLineDash(isSynd ? [] : [4, 4]);
        ctx.stroke();
        ctx.setLineDash([]);
        ctx.globalAlpha = 1.0;

        // Cluster Bubble Title Tag
        ctx.fillStyle = color;
        ctx.font = "bold 11px Playfair Display";
        ctx.textAlign = "center";
        const tagText = isSynd ? `Story Cluster #${parseInt(cid) + 1} (${info.count} outlets)` : `Independent Origin`;
        ctx.fillText(tagText, hub.x, hub.y - bubbleRad - 8);
    });

    // 2. Draw Connecting Similarity Edges
    filteredEdges.forEach(edge => {
        const srcNode = nodePositions[edge.source];
        const tgtNode = nodePositions[edge.target];
        if (srcNode && tgtNode) {
            ctx.beginPath();
            ctx.moveTo(srcNode.x, srcNode.y);
            ctx.lineTo(tgtNode.x, tgtNode.y);
            ctx.strokeStyle = srcNode.color;
            ctx.globalAlpha = Math.min(1.0, edge.similarity);
            ctx.lineWidth = 2.0;
            ctx.stroke();
            ctx.globalAlpha = 1.0;

            const midX = (srcNode.x + tgtNode.x) / 2;
            const midY = (srcNode.y + tgtNode.y) / 2;
            ctx.fillStyle = "#1a1a1a";
            ctx.font = "9px Inter";
            ctx.textAlign = "center";
            ctx.fillText(`${Math.round(edge.similarity * 100)}%`, midX, midY - 3);
        }
    });

    // 3. Draw News Outlet Nodes
    nodePositions.forEach(n => {
        ctx.beginPath();
        ctx.arc(n.x, n.y, n.radius + 4, 0, 2 * Math.PI);
        ctx.fillStyle = n.color;
        ctx.globalAlpha = 0.2;
        ctx.fill();
        ctx.globalAlpha = 1.0;

        ctx.beginPath();
        ctx.arc(n.x, n.y, n.radius, 0, 2 * Math.PI);
        ctx.fillStyle = n.color;
        ctx.fill();
        ctx.strokeStyle = "#ffffff";
        ctx.lineWidth = 2;
        ctx.stroke();

        ctx.fillStyle = "#1a1a1a";
        ctx.font = "600 11px Inter";
        ctx.textAlign = "center";
        const domainClean = (n.domain || "source").replace("www.", "").split(".")[0];
        ctx.fillText(domainClean.toUpperCase(), n.x, n.y + n.radius + 14);
    });

    // Hover Tooltip Listener
    const tooltip = document.getElementById("bubble-tooltip");
    canvas.onmousemove = (e) => {
        const rect = canvas.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;

        let hoverNode = null;
        for (let n of nodePositions) {
            const dist = Math.hypot(n.x - mouseX, n.y - mouseY);
            if (dist <= n.radius + 6) {
                hoverNode = n;
                break;
            }
        }

        if (hoverNode && tooltip) {
            tooltip.innerHTML = `
                <div style="font-family:'Playfair Display'; font-weight:700; color:#00845a;"><i class="fa-solid fa-newspaper"></i> ${escapeHtml(hoverNode.title)}</div>
                <div style="margin-top:6px; font-size:0.78rem; color:#555;">
                    <div><strong>Domain:</strong> ${escapeHtml(hoverNode.domain)}</div>
                    <div><strong>Cluster:</strong> Story Cluster #${hoverNode.cluster_id + 1}</div>
                    <div><strong>Similarity Match Threshold (\(\tau\)):</strong> ${threshold.toFixed(2)}</div>
                </div>
            `;
            tooltip.style.left = `${Math.min(width - 280, mouseX + 15)}px`;
            tooltip.style.top = `${Math.max(10, mouseY - 50)}px`;
            tooltip.classList.remove("hidden");
        } else if (tooltip) {
            tooltip.classList.add("hidden");
        }
    };

    canvas.onmouseleave = () => {
        if (tooltip) tooltip.classList.add("hidden");
    };
}

// -------------------------------------------------------------
// 5. Render Synthesis Summary Report
// -------------------------------------------------------------
function renderSummaryReport(data) {
    document.getElementById("report-claim").innerText = `"${data.claim}"`;
    document.getElementById("report-trust-val").innerText = `${data.preliminary_trust_score}%`;

    const verdict = data.final_verdict;
    const badgeEl = document.getElementById("report-verdict-badge");
    badgeEl.className = "verdict-badge";
    if (verdict === "Real") {
        badgeEl.classList.add("badge-real");
        badgeEl.innerHTML = `<i class="fa-solid fa-circle-check"></i> REAL`;
    } else if (verdict === "Fake") {
        badgeEl.classList.add("badge-fake");
        badgeEl.innerHTML = `<i class="fa-solid fa-circle-xmark"></i> FAKE`;
    } else {
        badgeEl.classList.add("badge-unverified");
        badgeEl.innerHTML = `<i class="fa-solid fa-circle-exclamation"></i> UNVERIFIED`;
    }

    const scores = data.module_confidence_scores || {};
    document.getElementById("report-c1-val").innerText = `${Math.round((scores.module1_content_confidence || 0) * 100)}%`;
    document.getElementById("report-c2-val").innerText = `${Math.round((scores.module2_evidence_confidence || 0) * 100)}%`;
    document.getElementById("report-c3-val").innerText = `${(scores.module3_independence_confidence || 0).toFixed(4)}`;
}

function showLoader() {
    document.getElementById("loader-section").classList.remove("hidden");
}

function hideLoader() {
    document.getElementById("loader-section").classList.add("hidden");
}

function showResults() {
    document.getElementById("results-dashboard").classList.remove("hidden");
}

function hideResults() {
    document.getElementById("results-dashboard").classList.add("hidden");
}

function showError(msg) {
    const errorBox = document.getElementById("error-box");
    errorBox.innerText = msg;
    errorBox.classList.remove("hidden");
}

function hideError() {
    const errorBox = document.getElementById("error-box");
    errorBox.classList.add("hidden");
}

function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}
