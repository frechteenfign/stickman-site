import os
import asyncio
import requests
import edge_tts
import streamlit as st
from moviepy.editor import ImageClip, AudioFileClip

# إعدادات شكل الموقع
st.set_page_config(page_title="مصنع ستيك مان", page_icon="🎬")

st.title("🎬 مصنع فيديوهات الـ Stickman")
st.write("اكتب قصة قصيرة ووصف المشهد لتوليد الفيديو!")

# صناديق الكتابة للمستخدم
story_text = st.text_area("✍️ اكتب نص القصة (بالعربي):")
image_prompt = st.text_input("👁️ وصف المشهد (بالإنجليزي):")

# زر التشغيل
if st.button("🚀 ابدأ التوليد"):
    if not story_text or not image_prompt:
        st.error("⚠️ يرجى ملء الحقول أولاً!")
    else:
        tmp_image = "temp_stickman.jpg"
        tmp_audio = "temp_voice.mp3"
        final_video = "stickman_shorts.mp4"
        
        with st.spinner("⏳ جاري صنع الفيديو... انتظر دقيقة"):
            try:
                # 1. توليد الصورة
                style_booster = ", dark horror stickman style, black background, 4k"
                cleaned_prompt = (image_prompt + style_booster).replace(" ", "%20")
                img_url = f"https://image.pollinations.ai/p/{cleaned_prompt}?width=720&height=1280"
                
                img_res = requests.get(img_url)
                with open(tmp_image, "wb") as f:
                    f.write(img_res.content)
                
                # 2. توليد الصوت
                communicate = edge_tts.Communicate(story_text, "ar-EG-ShakirNeural")
                asyncio.run(communicate.save(tmp_audio))
                
                # 3. دمج الفيديو
                audio_clip = AudioFileClip(tmp_audio)
                image_clip = ImageClip(tmp_image).set_duration(audio_clip.duration)
                video_clip = image_clip.set_audio(audio_clip)
                video_clip.write_videofile(final_video, fps=24, codec="libx264", audio_codec="aac", logger=None)
                
                audio_clip.close()
                image_clip.close()
                video_clip.close()
                
                # عرض النتيجة
                st.success("🎉 تم صنع الفيديو بنجاح!")
                st.video(final_video)
                
                # حذف الملفات المؤقتة
                if os.path.exists(tmp_image): os.remove(tmp_image)
                if os.path.exists(tmp_audio): os.remove(tmp_audio)
                
            except Exception as e:
                st.error(f"❌ حدث خطأ: {e}")