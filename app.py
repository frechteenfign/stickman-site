import os
import asyncio
import requests
import edge_tts
import streamlit as st
from moviepy.editor import ImageClip, AudioFileClip

# Page Configuration
st.set_page_config(page_title="Stickman Factory", page_icon="🎬")

st.title("🎬 Stickman Video Factory")
st.write("Write a short story and describe the scene to generate your horror video!")

# User Inputs
story_text = st.text_area("✍️ Write your Story Script:")
image_prompt = st.text_input("👁️ Describe the Scene / Image Prompt:")

# Video Duration Selection
video_type = st.radio(
    "⏳ Video Duration & Format:",
    ["Under 1 minute (Vertical - TikTok / Shorts)", "Over 1 minute (Horizontal - YouTube Long-form)"]
)

# Run Button
if st.button("🚀 Start Generation"):
    if not story_text or not image_prompt:
        st.error("⚠️ Please fill in all fields first!")
    else:
        tmp_image = "temp_stickman.jpg"
        tmp_audio = "temp_voice.mp3"
        final_video = "stickman_shorts.mp4"
        
        with st.spinner("⏳ Creating your video... Please wait a moment"):
            try:
                # Set dimensions based on the chosen format
                if "Under 1 minute" in video_type:
                    width, height = 720, 1280 # Vertical for Shorts/TikTok
                else:
                    width, height = 1280, 720 # Horizontal for YouTube Long-form

                # 1. Generate Image using Pollinations AI
                style_booster = ", dark horror stickman style, black background, 4k"
                cleaned_prompt = (image_prompt + style_booster).replace(" ", "%20")
                img_url = f"https://image.pollinations.ai/p/{cleaned_prompt}?width={width}&height={height}"
                
                img_res = requests.get(img_url)
                with open(tmp_image, "wb") as f:
                    f.write(img_res.content)
                
                # 2. Generate Voiceover (Deep English Voice)
                communicate = edge_tts.Communicate(story_text, "en-US-BrianNeural")
                asyncio.run(communicate.save(tmp_audio))
                
                # 3. Merge Video and Audio
                audio_clip = AudioFileClip(tmp_audio)
                image_clip = ImageClip(tmp_image).set_duration(audio_clip.duration)
                video_clip = image_clip.set_audio(audio_clip)
                video_clip.write_videofile(final_video, fps=24, codec="libx264", audio_codec="aac", logger=None)
                
                audio_clip.close()
                image_clip.close()
                video_clip.close()
                
                # Display the final video
                st.success("🎉 Video created successfully!")
                st.video(final_video)
                
                # Clean up temporary files
                if os.path.exists(tmp_image): os.remove(tmp_image)
                if os.path.exists(tmp_audio): os.remove(tmp_audio)
                
            except Exception as e:
                st.error(f"❌ An error occurred: {e}")
