import os
import tempfile
import shutil
from flask import Flask, render_template, request, jsonify, send_file, abort
from yt_dlp import YoutubeDL
from urllib.parse import urlparse
import threading

app = Flask(__name__)

# yt-dlp options used for getting info only (no download)
YDL_OPTS_INFO = {
    'skip_download': True,
    'quiet': True,
    'no_warnings': True,
}

# helper: get video info (formats) using yt-dlp
def get_video_info(url):
    with YoutubeDL(YDL_OPTS_INFO) as ydl:
        info = ydl.extract_info(url, download=False)
    return info

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/info')
def api_info():
    url = request.args.get('url')
    if not url:
        return jsonify({ 'error': 'No url provided' }), 400

    try:
        info = get_video_info(url)

        # build a minimal formats list to return to frontend
        formats = []
        for f in info.get('formats', [])[::-1]:  # reversed to prefer higher quality last so we can pick easily
            # only include formats that have either video+audio or audio-only
            fmt = {
                'format_id': f.get('format_id'),
                'ext': f.get('ext'),
                'vcodec': f.get('vcodec'),
                'acodec': f.get('acodec'),
                'format_note': f.get('format_note'),
                'height': f.get('height'),
                'width': f.get('width'),
                'filesize': f.get('filesize') or f.get('filesize_approx'),
                'tbr': f.get('tbr'),
            }
            formats.append(fmt)

        return jsonify({
            'id': info.get('id'),
            'title': info.get('title'),
            'uploader': info.get('uploader'),
            'duration': info.get('duration'),
            'formats': formats,
        })

    except Exception as e:
        app.logger.exception('Error fetching info')
        return jsonify({ 'error': str(e) }), 500


# Download endpoint: downloads chosen format to a temp file then returns it
@app.route('/download')
def download():
    url = request.args.get('url')
    format_id = request.args.get('format_id')
    if not url or not format_id:
        return jsonify({ 'error': 'url and format_id are required' }), 400

    # Create a temp directory to store download
    tmpdir = tempfile.mkdtemp(prefix='vd_')
    try:
        # Build output template in temp dir
        out_template = os.path.join(tmpdir, '%(title)s.%(ext)s')

        ydl_opts = {
            'format': format_id,
            'outtmpl': out_template,
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            # Use progress hooks if you want to track progress
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        # find the downloaded file in tmpdir
        downloaded_files = [os.path.join(tmpdir, f) for f in os.listdir(tmpdir)]
        if not downloaded_files:
            app.logger.error('No file downloaded')
            return jsonify({ 'error': 'Download failed' }), 500

        # pick first file
        file_path = downloaded_files[0]

        # send file as attachment; Flask will stream it
        return send_file(file_path, as_attachment=True, download_name=os.path.basename(file_path))

    except Exception as e:
        app.logger.exception('Download error')
        return jsonify({ 'error': str(e) }), 500

    finally:
        # Clean up temp directory in a separate thread so response isn't blocked by cleanup
        def cleanup_dir(path):
            try:
                shutil.rmtree(path)
            except Exception:
                pass

        threading.Thread(target=cleanup_dir, args=(tmpdir,)).start()


if __name__ == '__main__':
    # For local testing only
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
