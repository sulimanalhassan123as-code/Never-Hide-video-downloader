# Advanced Video Downloader (yt-dlp inside server)

This project runs `yt-dlp` inside your Flask server to provide a reliable video downloader with format selection.

## Files
- `app.py` — Flask app with `/api/info` and `/download` endpoints
- `templates/index.html` — frontend
- `requirements.txt` — pip packages
- `Procfile` — gunicorn start command
- `Aptfile` — system packages (ffmpeg)

## Deploy on Render (recommended)
1. Push repo to GitHub.
2. Create a *New Web Service* in Render and connect the repo.
3. Render will detect Python. Configure build/start commands:
   - Build command (optional): `pip install -r requirements.txt`
   - Start command (Render will use the Procfile; ensure it's `web: gunicorn app:app --timeout 120`)
4. Add `Aptfile` to root so Render installs `ffmpeg`.

## Notes
- Downloads are performed on the server and streamed to the client. Large downloads may be slow depending on server resources and timeouts.
- You can increase Gunicorn timeout in `Procfile` if needed.
- If you expect heavy usage, consider using background jobs and object storage (S3) to hold files rather than streaming directly.
