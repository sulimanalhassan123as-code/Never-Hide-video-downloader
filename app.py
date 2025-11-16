from flask import Flask, render_template, request, redirect, url_for
import requests # The library to make HTTP requests

app = Flask(__name__)

# The URL for the public Cobalt API
COBALT_API_URL = "https://co.wuk.sh/api/json"

@app.route('/')
def index():
    """Renders the homepage."""
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    """Sends the user's URL to the Cobalt API and redirects to the result."""
    video_url = request.form['video_url']
    
    if not video_url:
        return redirect(url_for('index'))

    try:
        # Prepare the data to send to the Cobalt API
        # We are asking for the best quality video download
        payload = {
            "url": video_url,
            "vQuality": "1080", # You can change this to 720, 480 etc.
            "isNoTTWatermark": True
        }

        # Send a POST request to the Cobalt API
        response = requests.post(COBALT_API_URL, json=payload)
        response.raise_for_status() # This will raise an error if the request failed

        # Get the JSON data from the response
        data = response.json()

        # Check the status from the API and redirect to the download URL
        if data.get("status") == "stream":
            download_url = data.get("url")
            return redirect(download_url)
        else:
            # If the API returns an error or something else, go back home
            print(f"API returned an error: {data.get('text')}")
            return redirect(url_for('index'))

    except Exception as e:
        # If our request to the API fails, print the error and go back home
        print(f"An error occurred: {e}")
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
