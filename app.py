from flask import Flask, render_template, request, redirect, url_for
import requests

app = Flask(__name__)

# The correct and working API URL for Cobalt
COBALT_API_URL = "https://api.cobalt.tools/api/json"

@app.route('/')
def index():
    """Renders the homepage."""
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    """Sends a simplified, robust request to the Cobalt API."""
    video_url = request.form['video_url']
    
    if not video_url:
        return redirect(url_for('index'))

    try:
        # Prepare the simplest possible payload.
        # We only send the URL and let Cobalt figure out the best quality.
        payload = {
            "url": video_url
        }

        # Send the POST request with the correct headers
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        response = requests.post(COBALT_API_URL, headers=headers, json=payload)
        
        # Check if the request was successful
        response.raise_for_status() 

        # Get the JSON data from the response
        data = response.json()

        # Check the status from the API and redirect to the download URL
        if data.get("status") == "stream":
            download_url = data.get("url")
            return redirect(download_url)
        else:
            # If the API returns an error (e.g., link is invalid), handle it
            print(f"API returned an error: {data.get('text')}")
            return redirect(url_for('index'))

    except Exception as e:
        # If our request to the API fails, print the error and go back home
        print(f"An error occurred: {e}")
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
