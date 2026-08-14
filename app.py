import os
from flask import Flask, render_template, request, jsonify
import config
from pipeline import ClaimVerificationPipeline

app = Flask(__name__)

# Initialize pipeline once on startup
print("Initializing Fake News Detection Server & Pipeline...")
pipeline = ClaimVerificationPipeline()

@app.route("/")
def index():
    return render_template("index.html")

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

@app.route("/api/samples", methods=["GET"])
def get_sample_claims():
    samples = [
        {"claim": "NASA's James Webb Space Telescope discovers water vapor on distant exoplanet", "category": "Real"},
        {"claim": "Secret government laser laboratory caused recent major hurricane outbreak", "category": "Fake"},
        {"claim": "Global renewable energy capacity grew by a record 50% in 2023, report finds", "category": "Real"},
        {"claim": "5G cell towers confirmed to cause memory loss and battery drain in humans", "category": "Fake"},
        {"claim": "Study suggests coffee drinkers live longer, but researchers aren't sure why", "category": "Unverified"}
    ]
    return jsonify(samples)

if __name__ == "__main__":
    app.run(host=config.SERVER_HOST, port=config.SERVER_PORT, debug=config.DEBUG)
