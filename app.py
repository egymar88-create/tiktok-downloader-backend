from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
import random

app = Flask(__name__)
CORS(app)  # مهم جداً للسماح بالاتصال من Netlify

TEMP_FOLDER = 'temp_videos'
if not os.path.exists(TEMP_FOLDER):
    os.makedirs(TEMP_FOLDER)

@app.route('/download', methods=['GET', 'POST'])
def download_video():
    if request.method == 'POST':
        data = request.json
        url = data.get('url')
    else:
        url = request.args.get('url')

    if not url:
        return jsonify({"status": "error", "error": "الرابط مطلوب"}), 400

    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
    ]

    filename = f"{random.randint(1000, 9999)}.mp4"
    filepath = os.path.join(TEMP_FOLDER, filename)

    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'outtmpl': filepath,
        'http_headers': {
            'User-Agent': random.choice(user_agents),
            'Referer': 'https://www.tiktok.com/',
        },
        'no_check_certificate': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True, download_name=f"video_no_watermark.mp4")
        else:
            return jsonify({"status": "error", "error": "فشل التحميل"}), 500

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"status": "error", "error": "خطأ في المعالجة"}), 500

# هذا السطر هو الأهم لـ Railway و Render
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
