from flask import Flask, render_template, request, send_file, redirect, url_for, session
from pytube import YouTube
import io

# Initialize the Flask app
app = Flask(__name__)
# A secret key is needed for session management to store flash messages.
# Replace 'your_secret_key' with a random string.
app.secret_key = 'your_secret_key' 

@app.route('/')
def index():
    """
    Renders the main page of the web application.
    """
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    """
    Handles the video download logic.
    """
    video_url = request.form['video_url']
    if not video_url:
        # If the user submits an empty form, redirect them back to the homepage
        return redirect(url_for('index'))

    try:
        # Create a YouTube object
        yt = YouTube(video_url)

        # Get the highest resolution progressive stream (video + audio)
        stream = yt.streams.get_highest_resolution()

        # Download the video into a memory buffer
        buffer = io.BytesIO()
        stream.stream_to_buffer(buffer)
        buffer.seek(0)

        # Use a safe filename from the video title
        safe_filename = "".join([c for c in yt.title if c.isalpha() or c.isdigit() or c.isspace()]).rstrip()

        # Send the buffer as a file attachment for the user to download
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"{safe_filename}.mp4",
            mimetype="video/mp4"
        )

    except Exception as e:
        # Handle errors (e.g., invalid URL, private video, etc.)
        # For simplicity, we'll just print the error and redirect back home.
        # A more advanced app would show a specific error message to the user.
        print(f"An error occurred: {e}")
        return redirect(url_for('index'))

# This part is for running the app in a development environment (like Replit's "Run" button)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
