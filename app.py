from flask import Flask, request, send_file
from flask_cors import CORS
import yt_dlp
import os
import random
import time

app = Flask(__name__)
CORS(app)  # مهم جداً للسماح بالاتصال من Netlify أو أي دومين آخر

# مجلد لتخزين الفيديوهات مؤقتاً
TEMP_FOLDER = 'temp_videos'
if not os.path.exists(TEMP_FOLDER):
    os.makedirs(TEMP_FOLDER)

@app.route('/download', methods=['GET'])
def download_video():
    url = request.args.get('url')
    if not url:
        return "الرابط مطلوب", 400

    # تنظيف الملفات القديمة كل مرة (اختياري لكن مفيد)
    cleanup_old_files()

    # اسم ملف عشوائي لتجنب التعارض
    filename = f"{random.randint(10000, 99999)}.mp4"
    filepath = os.path.join(TEMP_FOLDER, filename)

    # قائمة User-Agents عشوائية لتبدو كأننا متصفحات حقيقية
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1'
    ]

    # إعدادات yt-dlp المتقدمة لتجنب الحظر وتحسين الأداء
    ydl_opts = {
        'format': 'best[ext=mp4]',  # نفضل MP4 فقط لتجنب مشاكل التنسيقات الأخرى
        'quiet': True,              # لا تظهر مخرجات في التيرمينال
        'no_warnings': True,        # لا تحذيرات
        'outtmpl': filepath,        # مسار حفظ الملف
        'http_headers': {           # رؤوس HTTP لمحاكاة متصفح حقيقي
            'User-Agent': random.choice(user_agents),
            'Referer': 'https://www.tiktok.com/',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        },
        'no_check_certificate': True,  # تجاهل أخطاء الشهادات (مهم لبعض الروابط)
        'sleep_interval': 2,           # تأخير بين الطلبات لتجنب الحظر
        'max_sleep_interval': 5,       # أقصى تأخير
        'extractor_args': {            # خيارات إضافية لـ TikTok
            'tiktok': ['api_hostname=api-h2.tiktokv.com']
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # التحقق من أن الملف تم إنشاؤه بنجاح
        if os.path.exists(filepath):
            # إرسال الملف للمستخدم كرابط تنزيل مباشر
            return send_file(
                filepath,
                mimetype='video/mp4',
                as_attachment=True,
                download_name=f'tiktok_no_watermark_{filename}.mp4',
                conditional=True  # يدعم الاستئناف والتخزين المؤقت — مهم جداً للملفات الكبيرة
            )
        else:
            return "فشل تحميل الفيديو من المصدر — الملف غير موجود", 500

    except Exception as e:
        print(f"❌ Error downloading {url}: {str(e)}")
        return f"حدث خطأ أثناء التحميل: {str(e)}", 500


def cleanup_old_files():
    """
    حذف الملفات الأقدم من ساعة واحدة لتوفير المساحة على السيرفر.
    مهم لأن الخطة المجانية على Railway لها مساحة محدودة.
    """
    try:
        now = time.time()
        for fname in os.listdir(TEMP_FOLDER):
            fpath = os.path.join(TEMP_FOLDER, fname)
            # إذا كان الملف أقدم من 3600 ثانية (ساعة)، احذفه
            if os.path.isfile(fpath) and now - os.path.getmtime(fpath) > 3600:
                os.remove(fpath)
                print(f"🗑️ Deleted old file: {fname}")
    except Exception as e:
        print(f"⚠️ Cleanup error: {e}")


# تشغيل السيرفر — متوافق مع Railway, Render, Heroku, etc.
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
