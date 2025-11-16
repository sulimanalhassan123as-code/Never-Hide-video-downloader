from flask import Flask, render_template, request, jsonify
import requests
from urllib.parse import quote

app = Flask(__name__)

API_ENDPOINT = "https://api.ryzendesu.com/info?url="  # More stable

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/get_video_info")
def get_video_info():
    video_url = request.args.get("url")

    if not video_url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        safe_url = quote(video_url, safe="")
        full_api_url = f"{API_ENDPOINT}{safe_url}"

        response = requests.get(
            full_api_url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=15
        )
        response.raise_for_status()

        return jsonify(response.json())

    except Exception as e:
        return jsonify({"error": str(e)}), 500
