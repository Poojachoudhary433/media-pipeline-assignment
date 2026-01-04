from deep_translator import GoogleTranslator
import os

INPUT_SRT = "subtitles_en.srt"
OUTPUT_DIR = "subtitles"

languages = {
    "hi": "Hindi",
    "ta": "Tamil",
    "te": "Telugu",
    "kn": "Kannada",
    "ml": "Malayalam",
    "mr": "Marathi",
    "bn": "Bengali",
    "gu": "Gujarati",
    "pa": "Punjabi",
    "ur": "Urdu",
    "fr": "French",
    "es": "Spanish",
    "de": "German",
    "ar": "Arabic",
    "ja": "Japanese",
    "ko": "Korean",
    "zh-CN": "Chinese"
}

os.makedirs(OUTPUT_DIR, exist_ok=True)

def translate_srt(lang_code):
    translator = GoogleTranslator(source="en", target=lang_code)
    output_file = f"{OUTPUT_DIR}/subtitles_{lang_code}.srt"

    with open(INPUT_SRT, "r", encoding="utf-8") as f:
        lines = f.readlines()

    translated_lines = []
    for line in lines:
        if "-->" in line or line.strip().isdigit() or line.strip() == "":
            translated_lines.append(line)
        else:
            translated_lines.append(translator.translate(line.strip()) + "\n")

    with open(output_file, "w", encoding="utf-8") as f:
        f.writelines(translated_lines)

    print(f" Created {output_file}")

for code in languages:
    translate_srt(code)
