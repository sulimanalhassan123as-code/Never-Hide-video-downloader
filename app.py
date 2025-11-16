from flask import Flask, render_template, request, redirect, url_for
import requests

app = Flask(__name__)

# This is a public API that uses the powerful yt-dlp library in the background.
# It is more direct and reliable for our purpose.
API_ENDPOINT = "https://yt-dlp-api.vercel.app/api/info?url="

@app.route('/')
def index():
    """Renders the homepage."""
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    """Uses the yt-dlp-api to get a direct download link."""
    video_url = request.form['video_url']
    
    if not video_url:
        return redirect(url_for('index'))

    try:
        # We append the user's video URL directly to the API endpoint URL.
        # This is a simple GET request, which is more reliable.
        full_api_url = f"{API_ENDPOINT}{video_url}"

        # Make the request to the API
        response = requests.get(full_api_url)
        response.raise_for_status()  # This will raise an error if the request failed

        # Get the JSON data from the response
        data = response.json()

        # The API gives us a list of available formats. We will find the best MP4.
        best_mp4_url = None
        for format in data.get("formats", []):
            # Look for a format that has both video and audio and is an mp4.
            if format.get("vcodec") != "none" and format.get("acodec") != "none" and format.get("ext") == "mp4":
                best_mp4_url = format.get("url")
                break # Stop after finding the first suitable format

        if best_mp4_url:
            # If we found a link, redirect the user's browser to it.
            return redirect(best_mp4_url)
        else:
            # If no suitable MP4 format was found, just go back to the homepage.
            print("No suitable MP4 format with video and audio found.")
            return redirect(url_for('index'))

    except Exception as e:
        print(f"An error occurred: {e}")
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
