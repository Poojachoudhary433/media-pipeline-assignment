import re
import json

INPUT_MD = "content/vector_spaces.md"
OUTPUT_JSON = "scripts/slides.json"

slides = []
current_slide = None

with open(INPUT_MD, "r", encoding="utf-8") as f:
    lines = f.readlines()

for line in lines:
    line = line.strip()

    # Detect new slide
    slide_match = re.match(r"# Slide (\d+)", line)
    if slide_match:
        if current_slide:
            slides.append(current_slide)

        current_slide = {
            "slide_number": int(slide_match.group(1)),
            "title": "",
            "content": [],
            "math": [],
            "images": [],
            "duration_min": 1
        }
        continue

    # Slide title
    if line.startswith("## ") and current_slide:
        current_slide["title"] = line.replace("## ", "")
        continue

    # Duration
    duration_match = re.search(r"\*\*Duration:\*\* ([\d\.]+) min", line)
    if duration_match and current_slide:
        current_slide["duration_min"] = float(duration_match.group(1))
        continue

    # Images
    image_match = re.search(r"!\[.*?\]\((.*?)\)", line)
    if image_match and current_slide:
        current_slide["images"].append(image_match.group(1))
        continue

    # Math (LaTeX block or inline)
    if "\\" in line and current_slide:
        current_slide["math"].append(line)
        continue

    # Bullet points or text
    if current_slide and line and not line.startswith("---"):
        current_slide["content"].append(line)

# Append last slide
if current_slide:
    slides.append(current_slide)

# Save JSON
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(slides, f, indent=4, ensure_ascii=False)

print("Markdown successfully converted to slides.json")
