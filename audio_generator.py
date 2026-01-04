import edge_tts
import asyncio
import re
import os

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------------------------
# UTILITY FUNCTIONS
# ---------------------------

def parse_duration(duration_str):
    """
    Converts '4 min' to 240 or '30 sec' to 30
    """
    if isinstance(duration_str, (int, float)):
        return int(duration_str)
    
    numbers = re.findall(r'\d+', str(duration_str))
    if not numbers:
        return 30  # fallback

    val = int(numbers[0])
    if "min" in str(duration_str).lower():
        return val * 60
    return val

def clean_text(text: str) -> str:
    """
    Removes markdown and symbols for clean narration
    """
    text = re.sub(r"\*\*", "", text)
    text = re.sub(r"[_`#>-]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def estimate_speech_rate(text: str, target_duration: int):
    """
    Estimate speaking rate to roughly match target duration.
    Returns a rate string for edge-tts.
    """
    words = len(text.split())
    if target_duration is None or target_duration <= 0:
        return "+0%"
    
    minutes = max(target_duration / 60, 0.5)  # Avoid division by zero
    needed_wpm = words / minutes

    # Standard speech ~150 WPM
    if needed_wpm < 100:
        return "-30%"
    elif needed_wpm > 200:
        return "+20%"
    else:
        return "+0%"

# ---------------------------
# MAIN AUDIO FUNCTION
# ---------------------------

async def generate_audio(
    text: str,
    filename: str,
    target_duration: int | None = None,
    voice: str = "en-US-ChristopherNeural"
):
    """
    Generates audio from text using edge-tts.
    Returns full path to saved file.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    text = clean_text(text)

    if isinstance(target_duration, str):
        target_duration = parse_duration(target_duration)

    rate_str = estimate_speech_rate(text, target_duration)

    filepath = os.path.join(OUTPUT_DIR, filename)

    try:
        communicate = edge_tts.Communicate(
            text=text,
            voice=voice,
            rate=rate_str
        )
        await communicate.save(filepath)
    except Exception as e:
        print(f"[Warning] edge-tts failed: {e}")
        # fallback silent audio if needed
        from pydub import AudioSegment
        silent = AudioSegment.silent(duration=1000)
        silent.export(filepath, format="mp3")

    # Verify file
    if not os.path.exists(filepath) or os.path.getsize(filepath) < 1000:
        raise RuntimeError(f"Audio generation failed or file too small: {filepath}")

    return filepath

# ---------------------------
# SYNC HELPER (for testing)
# ---------------------------
def generate_audio_sync(text, filename, target_duration=None, voice="en-US-ChristopherNeural"):
    return asyncio.run(generate_audio(text, filename, target_duration, voice))
