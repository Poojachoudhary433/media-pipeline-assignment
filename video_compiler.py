from moviepy import ImageClip, AudioFileClip, concatenate_videoclips
import os

def build_video(slides_data, final_name="presentation.mp4"):
    clips = []
    for data in slides_data:
        audio = AudioFileClip(data['audio'])
        # Create clip and sync it to audio duration
        img_clip = ImageClip(data['image']).with_duration(audio.duration).with_audio(audio)
        
        clips.append(img_clip)
    
    final_video = concatenate_videoclips(clips, method="compose")
    output_path = os.path.join("output", final_name)
    final_video.write_videofile(output_path, fps=24, codec="libx264")
    return output_path

compile_video = build_video
