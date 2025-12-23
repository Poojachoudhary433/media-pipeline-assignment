import edge_tts
import asyncio

async def generate_audio(text, filename):
    # 'en-US-ChristopherNeural' sounds like a professional narrator
    communicate = edge_tts.Communicate(text, "en-US-ChristopherNeural")
    filepath = f"output/{filename}"
    await communicate.save(filepath)
    return filepath
