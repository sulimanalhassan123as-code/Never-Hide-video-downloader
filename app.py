from flask import Flask, render_template, request, jsonify
import requests
from urllib.parse import quote

app = Flask(__name__)

API_ENDPOINT = "https://yt-dlp-api.vercel.app/api/info?url="

@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template('index.html')

@app.route('/api/get_video_info')
def get_video_info_proxy():
    """
    This acts as a proxy. It takes a URL from our own frontend,
    calls the external API, and then sends the result back to our frontend.
    This avoids all CORS issues.
    """
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        # Encode the URL to ensure it's safe to pass to the API
        safe_video_url = quote(video_url, safe='')
        full_api_url = f"{API_ENDPOINT}{safe_video_url}"

        # Server makes the request to the external API
        response = requests.get(full_api_url)
        response.raise_for_status() # Raise an error for bad responses (4xx or 5xx)

        # Return the successful JSON response from the API back to our JavaScript
        return jsonify(response.json())

    except requests.exceptions.HTTPError as http_err:
        # Handle specific HTTP errors from the API
        return jsonify({"error": f"API returned an error: {http_err}"}), 502 # 502 Bad Gateway
    except Exception as e:
        # Handle other errors (like network issues)
        return jsonify({"error": f"An internal error occurred: {e}"}), 500
