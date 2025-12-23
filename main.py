from fastapi import FastAPI
from pydantic import BaseModel
import audio_generator
import image_generator
import video_compiler
import os

app = FastAPI()
os.makedirs("output", exist_ok=True)

class VideoRequest(BaseModel):
    title: str
    slides: list

@app.post("/generate-video")
async def start_pipeline(request: VideoRequest):
    processed = []
    
    for i, s in enumerate(request.slides):

        text_content = s.text if hasattr(s, 'text') else s['text']
        # Generate high-quality audio (Async)
        a_path = await audio_generator.generate_audio(text_content, f"a_{i}.mp3")
        # Generate styled slide
        i_path = image_generator.create_styled_slide(text_content, request.title, f"s_{i}.png")
        
        processed.append({"audio": a_path, "image": i_path})
    
    # Compile
    video_url = video_compiler.build_video(processed)
    
    return {"status": "Complete", "path": video_url}