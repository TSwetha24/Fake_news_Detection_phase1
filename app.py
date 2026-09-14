from flask import Flask, render_template, request, jsonify, send_file
import io
import config
from pipeline import ClaimVerificationPipeline
from src.module4_agentic_verification.pdf_generator import generate_pdf_report_bytes

app = Flask(__name__)

# Initialize pipeline once on startup
print("Initializing Fake News Detection Server & Pipeline...")
pipeline = ClaimVerificationPipeline()

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
    
    if not claim_text:
        return jsonify({"error": "Please enter a news claim or article headline."}), 400
        
    try:
        results = pipeline.process_claim(claim_text, target_evidence_count=15)
        return jsonify(results)
    except Exception as e:
        print(f"Error processing claim: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/download_report", methods=["POST"])
def download_report():
    data = request.get_json() or {}
    claim_text = data.get("claim", "").strip()
    
    if not claim_text:
        return jsonify({"error": "Please provide a valid claim to generate a report."}), 400
        
    try:
        verification_data = data.get("verification_data")
        if not verification_data:
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
