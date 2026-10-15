import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from flask import Flask, render_template, request, jsonify, send_file
import io
import os
import config

from pipeline import ClaimVerificationPipeline
from src.blockchain import Blockchain
from src.module4_agentic_verification.pdf_generator import generate_pdf_report_bytes

app = Flask(__name__)

# Initialize pipeline and blockchain ledger once on startup
print("Initializing Fake News Detection Server, Pipeline & Blockchain Ledger...")
pipeline = ClaimVerificationPipeline()
blockchain = Blockchain()

@app.route("/")
@app.route("/overview")
def index():
    return render_template("overview.html")

@app.route("/mod1")
def mod1_page():
    return render_template("mod1.html")

@app.route("/mod2")
def mod2_page():
    return render_template("mod2.html")

@app.route("/mod3")
def mod3_page():
    return render_template("mod3.html")

@app.route("/mod4")
def mod4_page():
    return render_template("mod4.html")

@app.route("/mod5")
def mod5_page():
    return render_template("mod5.html")

@app.route("/mod6")
def mod6_page():
    return render_template("mod6.html")

@app.route("/audit")
@app.route("/report")
def audit_page():
    return render_template("audit.html")

@app.route("/api/verify", methods=["POST"])
def verify_claim():
    data = request.get_json() or {}
    claim_text = data.get("claim", "").strip()
    force_reverify = data.get("force_reverify", False)
    
    if not claim_text:
        return jsonify({"error": "Please enter a news claim or article headline."}), 400
        
    try:
        # Step 1: Check Blockchain for previous verification record
        if not force_reverify:
            existing = blockchain.find_claim(claim_text)
            if os.getenv("DEBUG_TRACE"):
                from src.blockchain import Block
                c_hash = Block.hash_claim(claim_text)
                hit_info = f"Hit (Block #{existing[0].index})" if existing else "Miss"
                print(f"[DEBUG_TRACE] Claim: '{claim_text}' | Hash: {c_hash} | Cache: {hit_info}")
            if existing:
                block, cached_results = existing
                cached_results["cache_hit"] = True
                if "blockchain_info" in cached_results:
                    cached_results["blockchain_info"]["cache_hit"] = True
                    cached_results["blockchain_info"]["is_cached_in_blockchain"] = True
                print(f"Blockchain Cache Hit for claim '{claim_text[:30]}...' -> Block #{block.index}")
                return jsonify(cached_results)
        elif os.getenv("DEBUG_TRACE"):
            from src.blockchain import Block
            c_hash = Block.hash_claim(claim_text)
            print(f"[DEBUG_TRACE] Claim: '{claim_text}' | Hash: {c_hash} | Cache: Bypassed (force_reverify=True)")

        # Step 2: Run full verification pipeline if not found in blockchain or force_reverify is requested
        print(f"Running full verification pipeline for claim '{claim_text[:30]}...'")
        results = pipeline.process_claim(claim_text, target_evidence_count=15)
        results["cache_hit"] = False

        # Step 3: Mine and append new block to Blockchain
        new_block = blockchain.add_claim_block(claim_text, results)
        results["blockchain_info"] = {
            "is_cached_in_blockchain": False,
            "cache_hit": False,
            "just_mined": True,
            "block_index": new_block.index,
            "block_hash": new_block.hash,
            "previous_hash": new_block.previous_hash,
            "verified_at": new_block.timestamp,
            "nonce": new_block.nonce
        }
        return jsonify(results)

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error processing claim: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/blockchain/chain", methods=["GET"])
def get_blockchain_chain():
    return jsonify(blockchain.get_chain_summary())

@app.route("/api/blockchain/verify_chain", methods=["GET"])
def audit_blockchain_chain():
    is_valid = blockchain.is_chain_valid()
    return jsonify({
        "is_valid": is_valid,
        "total_blocks": len(blockchain.chain),
        "status": "SECURE_AND_TAMPER_PROOF" if is_valid else "TAMPER_DETECTED"
    })

@app.route("/api/download_report", methods=["POST"])
def download_report():
    data = request.get_json() or {}
    claim_text = data.get("claim", "").strip()
    
    if not claim_text:
        return jsonify({"error": "Please provide a valid claim to generate a report."}), 400
        
    try:
        verification_data = data.get("verification_data")
        if not verification_data:
            # Check blockchain first before running pipeline
            existing = blockchain.find_claim(claim_text)
            if existing:
                _, verification_data = existing
            else:
                verification_data = pipeline.process_claim(claim_text, target_evidence_count=15)
            
        pdf_buffer = generate_pdf_report_bytes(verification_data)
        
        safe_claim_snippet = "".join([c if c.isalnum() else "_" for c in claim_text[:30]]).strip("_")
        filename = f"TruthChain_Report_{safe_claim_snippet}.pdf"
        
        return send_file(
            pdf_buffer,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        print(f"Error generating PDF report: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/samples", methods=["GET"])
def get_sample_claims():
    samples = [
        {"claim": "Joseph Vijay is the CM of TamilNadu", "category": "Politics"},
        {"claim": "M K Stalin is the CM of TamilNadu", "category": "Politics"},
        {"claim": "NASA's James Webb Space Telescope discovers water vapor on distant exoplanet", "category": "Science"},
        {"claim": "Global renewable energy capacity grew by a record 50% in 2023, report finds", "category": "Environment"},
        {"claim": "5G cell towers confirmed to cause memory loss and battery drain in humans", "category": "Tech Rumors"}
    ]
    return jsonify(samples)

if __name__ == "__main__":
    app.run(host=config.SERVER_HOST, port=config.SERVER_PORT, debug=config.DEBUG)

