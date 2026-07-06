import os
import asyncio
import requests
import streamlit as st
import edge_tts
from moviepy.editor import ImageClip, AudioFileClip

# Page Configuration
st.set_page_config(page_title="Stickman Video Factory Pro", page_icon="🎬", layout="centered")

st.title("🎬 Stickman Video Factory Pro")
st.write("Generate clean animated stickman videos easily!")

# User Inputs
story_text = st.text_area("✍️ Write your Story Script:", placeholder="Hello everyone! Welcome to my video...")
video_prompt = st.text_input("👁️ Describe the Scene / Prompt:", placeholder="a classic black stickman figure walking in a clean park")

# Video Format Selection
video_type = st.radio(
    "⏳ Video Dimensions:",
    ["Vertical (TikTok / Shorts / Reels)", "Horizontal (YouTube Long-form)"]
)

# Run Button
if st.button("🚀 Generate AI Animated Video"):
    if not story_text or not video_prompt:
        st.error("⚠️ Please fill in both the script and prompt fields!")
    else:
        tmp_image = "temp_stickman.jpg"
        tmp_audio = "temp_voice.mp3"
        final_video = "stickman_final_animation.mp4"
        
        with st.spinner("⏳ Generating script voiceover and animating scene... Please wait..."):
            try:
                # Set aspect ratio dimensions
                if "Vertical" in video_type:
                    width, height = 720, 1280
                else:
                    width, height = 1280, 720

                # 1. Generate Voiceover using Edge-TTS
                communicate = edge_tts.Communicate(story_text, "en-US-BrianNeural")
                asyncio.run(communicate.save(tmp_audio))
                audio_clip = AudioFileClip(tmp_audio)
                
                # 2. Generate Professional Image via Pollinations AI (Stable Endpoint)
                style_booster = ", simple 2D vector style, clean minimalist background, flat design, cute character, 4k"
                cleaned_prompt = (video_prompt + style_booster).replace(" ", "%20")
                img_url = f"https://image.pollinations.ai/p/{cleaned_prompt}?width={width}&height={height}"
                
                img_res = requests.get(img_url)
                if img_res.status_code != 200:
                    raise Exception("Image generation service is currently busy. Please try again.")
                    
                with open(tmp_image, "wb") as f:
                    f.write(img_res.content)
                
                # 3. Animate the static character into a moving video clip
                # We apply a professional panning/zooming motion over time
                base_clip = ImageClip(tmp_image).set_duration(audio_clip.duration)
                
                # Applying a smooth slow cinematic zoom motion
                animated_clip = base_clip.resize(lambda t: 1 + 0.04 * t)
                
                final_video_clip = animated_clip.set_audio(audio_clip)
                
                # Render the final video
                final_video_clip.write_videofile(
                    final_video, 
                    fps=24, 
                    codec="libx264", 
                    audio_codec="aac", 
                    logger=None
                )
                
                # Close clips safely
                audio_clip.close()
                base_clip.close()
                animated_clip.close()
                final_video_clip.close()
                
                # Success output
                st.success("🎉 Professional Video Created Successfully!")
                st.video(final_video)
                
                # Clean up server temporary files
                if os.path.exists(tmp_image): os.remove(tmp_image)
                if os.path.exists(tmp_audio): os.remove(tmp_audio)
                
            except Exception as e:
                st.error(f"❌ Production Error: {e}")
