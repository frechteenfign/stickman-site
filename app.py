import os
import asyncio
import requests
import streamlit as st
import edge_tts
from moviepy.editor import VideoFileClip, AudioFileClip

# Page Configuration
st.set_page_config(page_title="Stickman Video Factory Pro", page_icon="🎬", layout="centered")

st.title("🎬 Stickman Video Factory Pro")
st.write("Generate real animated horror videos using advanced AI video models!")

# User Inputs
story_text = st.text_area("✍️ Write your Story Script:", placeholder="Once upon a time in a dark room...")
video_prompt = st.text_input("👁️ Describe the Video Motion / Prompt:", placeholder="a horror stickman running from a shadow monster")

# Video Format Selection
video_type = st.radio(
    "⏳ Video Dimensions:",
    ["Vertical (TikTok / Shorts / Reels)", "Horizontal (YouTube Long-form)"]
)

# Run Button
if st.button("🚀 Generate AI Animated Video"):
    if not story_text or not video_prompt:
        st.error("⚠️ Please fill in both the script and video prompt fields!")
    else:
        tmp_video = "temp_generated_video.mp4"
        tmp_audio = "temp_voice.mp3"
        final_video = "stickman_final_animation.mp4"
        
        with st.spinner("⏳ Harnessing AI Video Models... Generating motion and voiceover (This may take a minute)..."):
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
                
                # 2. Generate Real Animated Video via Pollinations Video AI
                # We feed the prompt with stickman horror modifiers
                style_booster = ", dark horror stickman animation style, scary motion, eerie atmosphere, 4k, fluid movement"
                cleaned_prompt = (video_prompt + style_booster).replace(" ", "%20")
                
                # Dynamic video endpoint with seed for unique motion
                video_url = f"https://video.pollinations.ai/p/{cleaned_prompt}?width={width}&height={height}&duration={int(audio_clip.duration)}"
                
                video_res = requests.get(video_url)
                if video_res.status_code != 200:
                    raise Exception("Video generation service is currently busy. Please try again.")
                    
                with open(tmp_video, "wb") as f:
                    f.write(video_res.content)
                
                # 3. Merge Generated Motion Video with the Voiceover
                base_video_clip = VideoFileClip(tmp_video)
                
                # Loop or adjust video duration to match the voice length exactly
                if base_video_clip.duration < audio_clip.duration:
                    final_video_clip = base_video_clip.loop(duration=audio_clip.duration)
                else:
                    final_video_clip = base_video_clip.subclip(0, audio_clip.duration)
                    
                final_video_clip = final_video_clip.set_audio(audio_clip)
                
                # Render the final masterpiece
                final_video_clip.write_videofile(
                    final_video, 
                    fps=24, 
                    codec="libx264", 
                    audio_codec="aac", 
                    logger=None
                )
                
                # Close clips safely
                audio_clip.close()
                base_video_clip.close()
                final_video_clip.close()
                
                # Success output
                st.success("🎉 Professional Animated Video Created Successfully!")
                st.video(final_video)
                
                # Clean up server temporary files
                if os.path.exists(tmp_video): os.remove(tmp_video)
                if os.path.exists(tmp_audio): os.remove(tmp_audio)
                
            except Exception as e:
                st.error(f"❌ Production Error: {e}")
