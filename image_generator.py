from PIL import Image, ImageDraw, ImageFont
import os

def create_styled_slide(text, title, filename):
    width, height = 1280, 720
    base = Image.new('RGB', (width, height), (20, 25, 35))
    draw = ImageDraw.Draw(base)

    # Define Colors
    title_color = (130, 170, 255)
    text_color = (240, 240, 240)
    card_color = (40, 45, 60)
    accent_blue = (100, 100, 255)

    # --- NEW: LOAD FONTS ---
    # Windows path to Arial. If you're on Mac, use "/Library/Fonts/Arial.ttf"
    try:
        font_path = "C:\\Windows\\Fonts\\arial.ttf"
        title_font = ImageFont.truetype(font_path, 50) # Big Title
        body_font = ImageFont.truetype(font_path, 35)  # Readable Body
    except:
        # Fallback if font isn't found
        title_font = ImageFont.load_default()
        body_font = ImageFont.load_default()

    # Draw the glassmorphism card
    card_shape = [100, 100, 1180, 620]
    draw.rounded_rectangle(card_shape, radius=20, fill=card_color)
    draw.rounded_rectangle(card_shape, radius=20, outline=accent_blue, width=2)

    # Draw Title with the NEW font
    draw.text((150, 140), title.upper(), fill=title_color, font=title_font)

    # Improved Word Wrap (Shortened line length for bigger text)
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        current_line.append(word)
        # We check roughly 40 characters now because the font is bigger
        if len(" ".join(current_line)) > 45:
            lines.append(" ".join(current_line))
            current_line = []
    lines.append(" ".join(current_line))

    # Draw Body Text with the NEW font
    y_text = 240
    for line in lines:
        draw.text((150, y_text), line, fill=text_color, font=body_font)
        y_text += 55 # Increased spacing for larger text

    path = os.path.join("output", filename)
    base.save(path)
    return path

generate_slide_image = create_styled_slide