import asyncio
import json
import uuid
import os
from main import run_video_pipeline, VideoRequest

async def main():
    # Load slides
    with open("slides.json", "r", encoding="utf-8") as f:
        slides_data = json.load(f)

    # Load narration
    with open("narration.json", "r", encoding="utf-8") as f:
        narration_data = json.load(f)

    # Merge narration into slides
    for i, slide in enumerate(slides_data["slides"]):
        # Create the key string (e.g., "slide_0", "slide_1")
        key = f"slide_{i}"
    
    # Check if the key exists in your narration.json
        if key in narration_data:
        # Get the text from the "voice_text" field
             slide["narration"] = narration_data[key].get("voice_text", "")
        else:
             print(f"Warning: No narration found for {key}")
             slide["narration"] = ""

    request_data = VideoRequest(**slides_data)

    job_id = str(uuid.uuid4())[:8]
    print(f"Starting pipeline with Job ID: {job_id}")

    await run_video_pipeline(request_data, job_id)

    print(f"Video created: output/presentation_{job_id}.mp4")

if __name__ == "__main__":
    asyncio.run(main())

