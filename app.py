import os
import tempfile
import shutil
import threading
from flask import Flask, render_template, request, jsonify, send_file
from yt_dlp import YoutubeDL

app = Flask(__name__)

# Options for retrieving info only
YDL_OPTS_INFO = {
    "skip_download": True,
    "quiet": True,
    "no_warnings": True,
}

def get_video_info(url):
    with YoutubeDL(YDL_OPTS_INFO) as ydl:
        info = ydl.extract_info(url, download=False)
    return info

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/info")
def api_info():
    url = request.args.get("url", "").strip()
    if not url:
        return jsonify({"error": "No url provided"}), 400

    try:
        info = get_video_info(url)
        # Build minimal formats info for frontend
        formats = []
        for f in info.get("formats", [])[::-1]:
            formats.append({
                "format_id": f.get("format_id"),
                "ext": f.get("ext"),
                "vcodec": f.get("vcodec"),
                "acodec": f.get("acodec"),
                "format_note": f.get("format_note"),
                "height": f.get("height"),
                "width": f.get("width"),
                "filesize": f.get("filesize") or f.get("filesize_approx"),
                "tbr": f.get("tbr"),
            })

        return jsonify({
            "id": info.get("id"),
            "title": info.get("title"),
            "uploader": info.get("uploader"),
            "duration": info.get("duration"),
            "formats": formats,
        })
    except Exception as e:
        app.logger.exception("Error fetching info")
        return jsonify({"error": str(e)}), 500

@app.route("/download")
def download():
    url = request.args.get("url", "").strip()
    format_id = request.args.get("format_id", "").strip()
    if not url or not format_id:
        return jsonify({"error": "url and format_id are required"}), 400

    tmpdir = tempfile.mkdtemp(prefix="vd_")
    try:
        out_template = os.path.join(tmpdir, "%(title)s.%(ext)s")
        ydl_opts = {
            "format": format_id,
            "outtmpl": out_template,
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        # Find downloaded file(s)
        files = [os.path.join(tmpdir, f) for f in os.listdir(tmpdir)]
        if not files:
            app.logger.error("No file downloaded in tmpdir")
            return jsonify({"error": "Download failed"}), 500

        # If multiple files, pick the largest (usually the merged file)
        files_sorted = sorted(files, key=lambda p: os.path.getsize(p), reverse=True)
        file_path = files_sorted[0]

        # Stream file to client as attachment
        filename = os.path.basename(file_path)
        return send_file(file_path, as_attachment=True, download_name=filename)
    except Exception as e:
        app.logger.exception("Download error")
        return jsonify({"error": str(e)}), 500
    finally:
        # Clean up in background thread
        def cleanup(path):
            try:
                shutil.rmtree(path)
            except Exception:
                pass
        threading.Thread(target=cleanup, args=(tmpdir,)).start()

if __name__ == "__main__":
    # Local debug server
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
