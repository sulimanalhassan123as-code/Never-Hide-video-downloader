from flask import Flask, render_template, request, redirect, url_for
import yt_dlp

app = Flask(__name__)

@app.route('/')
def index():
    """Renders the homepage."""
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    """Handles the video downloading logic using yt-dlp."""
    video_url = request.form['video_url']
    
    if not video_url:
        return redirect(url_for('index'))

    try:
        # These are the options for yt-dlp
        # We are asking for the best quality MP4 file that has both video and audio
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        }

        # Use yt-dlp to extract the video information WITHOUT downloading it
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            # From the extracted information, get the direct download URL
            download_url = info.get('url')

            if download_url:
                # Redirect the user's browser directly to the download link
                # This is much more efficient than sending the file from our server
                return redirect(download_url)
            else:
                # If for some reason a URL couldn't be found, go back to the homepage
                return redirect(url_for('index'))

    except Exception as e:
        # If any error occurs, print it for debugging and redirect the user
        print(f"An error occurred: {e}")
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
