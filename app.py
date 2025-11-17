@app.route("/api/get_formats")
def get_formats():
    video_url = request.args.get("url")
    if not video_url:
        return jsonify({"error": "URL missing"}), 400

    try:
        info = yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True}).extract_info(video_url, download=False)

        # Filter formats that contain BOTH video + audio
        merged = [
            f for f in info["formats"]
            if f.get("vcodec") != "none" and f.get("acodec") != "none"
        ]

        # If merged formats available
        if merged:
            merged_sorted = sorted(merged, key=lambda x: x.get("height", 0), reverse=True)
            best = merged_sorted[0]
            return jsonify({
                "status": "success",
                "url": best["url"],
                "ext": best["ext"],
                "height": best.get("height", "unknown")
            })

        # If none found: audio/video separate
        return jsonify({
            "status": "no_merged",
            "error": "This platform provides separate audio and video. You must merge them."
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
