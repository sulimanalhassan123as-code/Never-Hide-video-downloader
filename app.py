# Import the necessary libraries from Flask and Pytube
from flask import Flask, render_template, request, send_file, redirect, url_for
from pytube import YouTube
import io # io is used to handle the video data in memory

# Initialize the Flask web application
app = Flask(__name__)

# This is the main route for your website (e.g., your-app-name.com/)
@app.route('/')
def index():
    """Renders the homepage (the index.html template)."""
    return render_template('index.html')

# This route handles the download request from the form
@app.route('/download', methods=['POST'])
def download():
    """Handles the video downloading logic."""
    # Get the video URL submitted in the form
    video_url = request.form['video_url']
    
    # If the user clicks "Download" without pasting a URL, just send them back to the homepage
    if not video_url:
        return redirect(url_for('index'))

    try:
        # Create a YouTube object with the provided URL
        yt = YouTube(video_url)

        # Select the best available stream that includes both video and audio
        stream = yt.streams.get_highest_resolution()

        # Create a buffer in memory to hold the video file
        buffer = io.BytesIO()
        stream.stream_to_buffer(buffer)
        # Reset the buffer's position to the beginning to be ready for reading
        buffer.seek(0)

        # Create a clean, safe filename from the video's title
        safe_filename = "".join([c for c in yt.title if c.isalpha() or c.isdigit() or c.isspace()]).rstrip()
        
        # Send the video file from the buffer to the user's browser as a downloadable attachment
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"{safe_filename}.mp4",
            mimetype="video/mp4"
        )

    except Exception as e:
        # If any error occurs (e.g., invalid link, private video), print it for debugging
        # and redirect the user back to the homepage.
        print(f"An error occurred: {e}")
        return redirect(url_for('index'))

# This part is only for development (e.g., running on Replit) and will not be used by Railway/Render.
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
