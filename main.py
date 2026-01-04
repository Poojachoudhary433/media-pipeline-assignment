from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Union
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS
import audio_generator
import image_generator
import video_compiler
import os
import uuid   
import re
import json
from pathlib import Path

app = FastAPI()

# Create directories if not exist
os.makedirs("output/temp", exist_ok=True)

os.makedirs("subtitles", exist_ok=True)

# ---------------------------
# DATA MODELS
# ---------------------------

class ProjectMetadata(BaseModel):
    title: str
    author: str
    date: str
    total_duration: str

class Slide(BaseModel):
    slide_id: int
    title: str
    duration: str  # e.g., "1 min"
    subtitle: Optional[str] = None
    image: Optional[str] = None
    description: Optional[Union[str, List[str]]] = None
    code_block: Optional[str] = None
    math: Optional[List[str]] = None
    bullets: Optional[List[str]] = None
    steps: Optional[List[str]] = None
    concepts: Optional[List[str]] = None

class VideoRequest(BaseModel):
    project_metadata: ProjectMetadata
    slides: List[Slide]

# ---------------------------
# UTILITY FUNCTIONS
# ---------------------------

def parse_duration_to_seconds(duration_str: str) -> int:
    """Convert '4 min' to 240 or '30 sec' to 30 seconds."""
    try:
        numbers = re.findall(r'\d+', str(duration_str))
        if not numbers:
            return 30
        val = int(numbers[0])
        if "min" in str(duration_str).lower():
            return val * 60
        return val
    except:
        return 30

def get_narration_text(slide: Slide) -> str:
    """Collect all relevant text from a slide for audio generation."""
    text_parts = [slide.title]
    if slide.subtitle:
        text_parts.append(slide.subtitle)

    source = slide.description or slide.bullets or slide.steps or ""
    if isinstance(source, list):
        text_parts.extend(source)
    else:
        text_parts.append(source)

    # Clean markdown
    clean_text = ". ".join(text_parts).replace("**", "")
    return clean_text

def generate_subtitle_srt(slides_audio: List[dict], srt_file: str):
    """
    Generate a simple English .srt file from audio durations.
    slides_audio: [{"audio": audio_path, "text": narration_text}]
    """
    from mutagen.mp3 import MP3

    counter = 1
    current_time = 0
    lines = []

    for slide in slides_audio:
        audio_path = slide["audio"]
        text = slide["text"]
        if not os.path.exists(audio_path):
            continue

        audio = MP3(audio_path)
        duration_ms = int(audio.info.length * 1000)
        start_time = current_time
        end_time = start_time + duration_ms

        def ms_to_srt(ts_ms):
            ms = ts_ms % 1000
            s = (ts_ms // 1000) % 60
            m = (ts_ms // (1000 * 60)) % 60
            h = ts_ms // (1000 * 60 * 60)
            return f"{h:02}:{m:02}:{s:02},{ms:03}"

        lines.append(f"{counter}")
        lines.append(f"{ms_to_srt(start_time)} --> {ms_to_srt(end_time)}")
        lines.append(text)
        lines.append("")  # empty line
        counter += 1
        current_time = end_time

    with open(srt_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return srt_file

# ---------------------------
# VIDEO PIPELINE
# ---------------------------

async def run_video_pipeline(request: VideoRequest, job_id: str):
    processed = []
    slides_audio_for_srt = []
    project_title = request.project_metadata.title
    
    # ---------------------------
    # LOAD NARRATION ONCE
    # ---------------------------
    narration_map = {}

    if os.path.exists("narration.json"):
        with open("narration.json", "r", encoding="utf-8") as f:
            narration_data = json.load(f)

        for key, value in narration_data.items():
            try:
                slide_index = int(key.replace("slide_", ""))
                narration_map[slide_index] = value.get("voice_text", "").strip()
            except:
                continue

    print(f"[{job_id}] Starting Intro Slide...")

    # 1. INTRO SLIDE
    intro_text = f"Welcome to this presentation on {project_title}. Presented by {request.project_metadata.author}."
    intro_audio_path = f"temp/{job_id}_intro.mp3"
    await audio_generator.generate_audio(intro_text, intro_audio_path)
    
    intro_image_path = image_generator.create_styled_slide(
        body_text=f"By {request.project_metadata.author}",
        title_text=project_title,
        output_name=f"temp/{job_id}_intro.png",
        theme="intro"
    )

    processed.append({"audio": intro_audio_path, "image": intro_image_path})
    slides_audio_for_srt.append({"audio": intro_audio_path, "text": intro_text})

    # 2. CONTENT SLIDES
    for slide in request.slides:
        print(f"[{job_id}] Processing Slide {slide.slide_id}...")
        sec_duration = parse_duration_to_seconds(slide.duration)
        

        #  Priority: narration.json → fallback to slide text
        narration = narration_map.get(slide.slide_id)

        if not narration:
            narration = get_narration_text(slide)

        narration = narration.strip()

        #  Final safety check
        if not narration:
            narration = " "

        audio_file = f"temp/{job_id}_slide_{slide.slide_id}.mp3"
        audio_path = await audio_generator.generate_audio(
            narration, audio_file, target_duration=sec_duration
        )

        display_body = slide.bullets or slide.steps or slide.concepts or slide.description or ""
        image_file = f"temp/{job_id}_slide_{slide.slide_id}.png"
        image_path = image_generator.create_styled_slide(
            body_text=display_body,
            title_text=slide.title,
            code_block=slide.code_block,
            math=slide.math or [],
            images=[slide.image] if slide.image and os.path.exists(slide.image) else [],
            output_name=image_file,
            theme="content"
        )

        processed.append({
            "audio": audio_path,
            "image": image_path,
            "background": "assets/backgrounds/blue_gradient.mp4" if os.path.exists("assets/backgrounds/blue_gradient.mp4") else None
        })
        slides_audio_for_srt.append({"audio": audio_path, "text": narration})

    # 3. CREATE SUBTITLES
    srt_file = f"subtitles/{job_id}.srt"
    generate_subtitle_srt(slides_audio_for_srt, srt_file)
    print(f"[{job_id}] Subtitles generated: {srt_file}")

    # 4. BUILD FINAL VIDEO
    final_video_name = f"presentation_{job_id}.mp4"
    video_compiler.build_video(processed, subtitles_path=srt_file, final_name=final_video_name)
    print(f"[{job_id}] Video Complete: {final_video_name}")

# ---------------------------
# API ENDPOINT
# ---------------------------

@app.post("/generate-video")
async def start_pipeline(request: VideoRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())[:8]
    background_tasks.add_task(run_video_pipeline, request, job_id)
    return {
        "status": "Processing",
        "job_id": job_id,
        "message": "Video generation has started. Check logs for progress."
    }
