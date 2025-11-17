import os
import yt_dlp
import uuid
import subprocess
from flask import Flask, request, send_file, jsonify, render_template

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/download")
def download_video():
    video_url = request.args.get("url")
    if not video_url:
        return jsonify({"error": "No URL provided"}), 400

    # Unique file names to avoid conflicts
    video_id = str(uuid.uuid4())
    temp_video = f"video_{video_id}.mp4"
    temp_audio = f"audio_{video_id}.m4a"
    final_file = f"final_{video_id}.mp4"

    # yt-dlp options for separate download
    ydl_opts = {
        "outtmpl": "%(id)s",
        "quiet": True,
        "no_warnings": True,
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "postprocessors": [{
            "key": "FFmpegVideoConvertor",
            "preferedformat": "mp4"
        }]
    }

    try:
        # Download video+audio separately and merge automatically
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            filename = ydl.prepare_filename(info)
            ydl.download([video_url])

        # Find downloaded merged file
        downloaded = filename.replace(".webm", ".mp4").replace(".mkv", ".mp4")
        downloaded = downloaded.replace(".fvideo", ".mp4")

        # Serve the merged file
        return send_file(
            downloaded,
            as_attachment=True,
            download_name=f"{info.get('title','video')}.mp4",
            mimetype="video/mp4"
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        # Clean up files after download
        try:
            if os.path.exists(temp_video):
                os.remove(temp_video)
            if os.path.exists(temp_audio):
                os.remove(temp_audio)
        except:
            pass
