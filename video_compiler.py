from moviepy.config import change_settings
# Ensure this path matches your actual ImageMagick installation folder!
change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe"})

from moviepy.editor import (
    ImageClip,
    AudioFileClip,
    concatenate_videoclips,
    TextClip,
    CompositeVideoClip
)
from moviepy.video.tools.subtitles import SubtitlesClip
import os

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def build_video(slides, subtitles_path=None, final_name="presentation.mp4"):
    clips = []
    audio_clips = []  # 🔥 IMPORTANT
    # 1. Build individual slide clips
    for idx, slide in enumerate(slides):
        if not os.path.exists(slide["audio"]):
            print(f"[Warning] Missing audio: {slide['audio']}")
            continue

        if not os.path.exists(slide["image"]):
            print(f"[Warning] Missing image: {slide['image']}")
            continue

        audio = AudioFileClip(slide["audio"])
        audio_clips.append(audio)  # 🔥 KEEP REFERENCE
        duration = audio.duration

        if duration is None or duration <= 0:
            print(f"[Warning] Invalid duration for audio: {slide['audio']}")
            continue

        # MoviePy 2.0+ uses .with_duration and .with_audio
        # .resize is often now .resized
        clip = (
            ImageClip(slide["image"])
            .set_duration(duration) 
            .resize(width=1280, height=720)
            .set_audio(audio)
        )
        clips.append(clip)

    if not clips:
        raise RuntimeError("No valid clips to compile into a video.")

    # 2. Concatenate all slides
    final_video = concatenate_videoclips(clips, method="compose")

    # 3. Add subtitles overlay (Simplified Logic)
    if subtitles_path and os.path.exists(subtitles_path):
        print(f"Applying subtitles from: {subtitles_path}")
        
        def subtitle_generator(txt):
            return TextClip(
                txt, 
                font="Arial", 
                fontsize=36, 
                color="white", 
                stroke_color="black", 
                stroke_width=1,
                method='caption', # Helps with long text wrapping
                size=(1100, None)
            )

        subs = SubtitlesClip(subtitles_path, subtitle_generator)
        
        # Position subtitles at the bottom
        # Use CompositeVideoClip to layer subtitles over the video
        final_video = CompositeVideoClip([
            final_video, 
            subs.set_position(('center', 600)) 
        ])

    # 4. Write Final File
    output_path = os.path.join(OUTPUT_DIR, final_name)
    
    final_video.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        audio_fps=44100,   # 🔥 ADD THIS
        threads=4
    )

    # 🔥 CLEANUP
    final_video.close()
    for a in audio_clips:
        a.close()
    return output_path

# Alias
compile_video = build_video


