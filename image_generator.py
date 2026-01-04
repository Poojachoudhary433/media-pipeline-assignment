from PIL import Image, ImageDraw, ImageFont
import os
import textwrap

OUTPUT_DIR = "output"
ASSETS_DIR = "images"

WIDTH, HEIGHT = 1280, 720

# ---------------------------
# FONT LOADER
# ---------------------------
def load_fonts():
    try:
        font_path = "C:\\Windows\\Fonts\\arial.ttf"
        mono_path = "C:\\Windows\\Fonts\\consola.ttf"
        title_font = ImageFont.truetype(font_path, 52)
        body_font = ImageFont.truetype(font_path, 28)
        math_font = ImageFont.truetype(font_path, 32)
        code_font = ImageFont.truetype(mono_path, 17)
    except:
        title_font = ImageFont.load_default()
        body_font = ImageFont.load_default()
        math_font = ImageFont.load_default()
        code_font = ImageFont.load_default()
    return title_font, body_font, math_font, code_font

# ---------------------------
# THEME CONFIG
# ---------------------------
THEMES = {
    "intro": {
        "bg": (18, 24, 38),
        "card": (35, 42, 60),
        "title": (160, 200, 255),
        "text": (230, 230, 230)
    },
    "content": {
        "bg": (20, 25, 35),
        "card": (40, 45, 60),
        "title": (130, 170, 255),
        "text": (240, 240, 240)
    },
    "outro": {
        "bg": (15, 20, 30),
        "card": (30, 35, 50),
        "title": (255, 210, 130),
        "text": (240, 240, 240)
    }
}

# ---------------------------
# MAIN SLIDE CREATOR
# ---------------------------
def create_styled_slide(
    body_text=None,
    title_text="",
    math=None,
    images=None,
    code_block=None, 
    output_name="slide.png",
    theme="content"
):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    theme_cfg = THEMES.get(theme, THEMES["content"])
    title_font, body_font, math_font, code_font = load_fonts()

    # Base image
    base = Image.new("RGB", (WIDTH, HEIGHT), theme_cfg["bg"])
    draw = ImageDraw.Draw(base)

    # Card
    card_box = [40, 30, WIDTH - 40, HEIGHT - 30]
    draw.rounded_rectangle(card_box, radius=22, fill=theme_cfg["card"], outline=(90, 120, 200), width=2)

    # Title
    draw.text((80, 60), title_text, fill=theme_cfg["title"], font=title_font)

    # ---------------------------
    # CODE BLOCK (takes priority)
    # ---------------------------
    if code_block:
        code_lines = code_block.strip().split("\n")
        line_height = 22
        max_lines = 25
        if len(code_lines) > max_lines:
            line_height = 18  # shrink if too many lines

        # Inner box for code
        box_x1, box_y1 = 80, 130
        box_x2 = WIDTH - 80
        box_y2 = min(box_y1 + len(code_lines) * line_height + 30, HEIGHT - 50)
        draw.rounded_rectangle([box_x1, box_y1, box_x2, box_y2], radius=12, fill=(10, 15, 25), outline=(60, 80, 150), width=1)

        # Draw code lines
        curr_y = box_y1 + 15
        for line in code_lines:
            if curr_y + line_height > HEIGHT - 60:
                break
            draw.text((box_x1 + 20, curr_y), line, fill=(210, 230, 255), font=code_font)
            curr_y += line_height

    # ---------------------------
    # BODY TEXT (if no code block)
    # ---------------------------
    elif body_text:
        y_cursor = 160
        text_to_draw = body_text if isinstance(body_text, str) else " ".join(body_text)
        wrapped = textwrap.wrap(text_to_draw, width=70)
        for w in wrapped:
            draw.text((100, y_cursor), w, fill=theme_cfg["text"], font=body_font)
            y_cursor += 40

    # ---------------------------
    # MATH (text placeholders)
    # ---------------------------
    if math and not code_block:
        y_val = max(400, y_cursor + 20)
        for expr in math:
            draw.text((140, y_val), f"[Math] {expr}", fill=(200, 220, 255), font=math_font)
            y_val += 42

    # ---------------------------
    # IMAGES (stacked right side)
    # ---------------------------
    if images:
        img_x = WIDTH - 400
        img_y = 150 if not code_block else 400
        for img_name in images:
            img_path = img_name if os.path.exists(img_name) else os.path.join(ASSETS_DIR, os.path.basename(img_name))
            if os.path.exists(img_path):
                img = Image.open(img_path).convert("RGBA")
                img.thumbnail((300, 200))
                base.paste(img, (img_x, img_y), img)
                img_y += img.height + 20

    # Save final slide
    out_path = os.path.join(OUTPUT_DIR, output_name)
    base.save(out_path)
    return out_path

generate_slide_image = create_styled_slide
