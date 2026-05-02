from flask import Flask, request, send_file
from flask_cors import CORS
import yt_dlp
import os
import random
import time

app = Flask(__name__)
CORS(app)

TEMP_FOLDER = 'temp_videos'
if not os.path.exists(TEMP_FOLDER):
    os.makedirs(TEMP_FOLDER)

@app.route('/download', methods=['GET'])
def download_video():
    url = request.args.get('url')
    if not url:
        return "الرابط مطلوب", 400

    # تنظيف الروابط القديمة كل فترة (اختياري)
    cleanup_old_files()

    filename = f"{random.randint(10000, 99999)}.mp4"
    filepath = os.path.join(TEMP_FOLDER, filename)

    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    ]

    ydl_opts = {
        'format': 'best[ext=mp4]',
        'quiet': True,
        'no_warnings': True,
        'outtmpl': filepath,
        'http_headers': {
            'User-Agent': random.choice(user_agents),
            'Referer': 'https://www.tiktok.com/',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        },
        'no_check_certificate': True,
        'sleep_interval': 1,  # تأخير بين الطلبات لتجنب الحظر
        'max_sleep_interval': 3,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        if os.path.exists(filepath):
            # إرسال الملف للمستخدم
            return send_file(
                filepath,
                mimetype='video/mp4',
                as_attachment=True,
                download_name=f'tiktok_no_watermark_{filename}'
            )
        else:
            return "فشل تحميل الفيديو من المصدر", 500

    except Exception as e:
        print(f"Error downloading {url}: {str(e)}")
        return f"حدث خطأ أثناء التحميل: {str(e)}", 500

def cleanup_old_files():
    """حذف الملفات القديمة لتوفير المساحة"""
    try:
        now = time.time()
        for fname in os.listdir(TEMP_FOLDER):
            fpath = os.path.join(TEMP_FOLDER, fname)
            if os.path.isfile(fpath) and now - os.path.getmtime(fpath) > 3600:  # حذف بعد ساعة
                os.remove(fpath)
    except:
        pass

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
