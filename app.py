from flask import Flask, render_template, request, redirect, url_for
import requests
from urllib.parse import quote # Import the standard URL encoding function

app = Flask(__name__)

API_ENDPOINT = "https://yt-dlp-api.vercel.app/api/info?url="

@app.route('/')
def index():
    """Renders the homepage."""
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    """URL-encodes the video URL before sending it to the API."""
    video_url = request.form['video_url']
    
    if not video_url:
        return redirect(url_for('index'))

    try:
        # THE CRUCIAL FIX: URL-encode the user's video link to make it safe.
        safe_video_url = quote(video_url)

        # Append the now-safe video URL to the API endpoint.
        full_api_url = f"{API_ENDPOINT}{safe_video_url}"

        # Make the GET request to the API
        response = requests.get(full_api_url)
        response.raise_for_status()  # Check for HTTP errors

        data = response.json()

        best_mp4_url = None
        # Look for the best format that has video, audio, and is an mp4 file.
        for format in data.get("formats", []):
            if format.get("vcodec") != "none" and format.get("acodec") != "none" and format.get("ext") == "mp4":
                best_mp4_url = format.get("url")
                break # Found a good one, no need to look further

        if best_mp4_url:
            return redirect(best_mp4_url)
        else:
            # If a perfect mp4 isn't found, try to find ANY format with video and audio
            # This makes the app more robust for other sites.
            for format in data.get("formats", []):
                if format.get("vcodec") != "none" and format.get("acodec") != "none":
                    best_mp4_url = format.get("url")
                    break
            
            if best_mp4_url:
                return redirect(best_mp4_url)
            else:
                 print("No suitable downloadable format was found.")
                 return redirect(url_for('index'))

    except Exception as e:
        print(f"An error occurred: {e}")
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
