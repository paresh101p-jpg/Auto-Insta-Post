import os
import io
import json
import time
import base64
import random
import requests
from PIL import Image, ImageDraw, ImageFont
from instagrapi import Client
from google import genai
from google.genai import types

# Secrets from GitHub Actions
IG_USERNAME = os.environ.get("IG_USERNAME")
IG_SESSION = os.environ.get("IG_SESSION")  # Base64 encoded session
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not all([IG_USERNAME, IG_SESSION, GEMINI_API_KEY]):
    print("Error: Please set IG_USERNAME, IG_SESSION, and GEMINI_API_KEY as environment variables.")
    exit(1)

client = genai.Client(api_key=GEMINI_API_KEY)

# Instagram feed photos: 4:5 (1080x1350) is the safest vertical size.
# 9:16 (1080x1920) can get cropped/rejected for feed posts.
IMG_WIDTH, IMG_HEIGHT = 1080, 1350
IMAGE_PATH = "today_post.jpg"

# Only models that actually exist right now (old 2.0/1.5 return 404)
GEMINI_MODELS = ["gemini-3.6-flash"]


def generate_thought():
    print("Generating a trending Hindi thought using Gemini...")
    prompt = ("Write ONE deep, trending, and beautiful short Hindi thought/quote "
              "(max 10 words). Only return the Hindi text, nothing else.")
    for model_name in GEMINI_MODELS:
        for attempt in range(1, 6):
            try:
                print(f"Trying model: {model_name} (attempt {attempt})...")
                response = client.models.generate_content(model=model_name, contents=prompt)
                text = response.text.strip().replace('"', '')
                if text:
                    print(f"Today's thought: {text}")
                    return text
            except Exception as e:
                print(f"Model {model_name} failed: {e}")
                time.sleep(5 * attempt)  # 503 = busy, wait longer each time
    raise Exception("All Gemini attempts failed. Try again later.")


def build_image_prompt():
    # Background only - NO text in prompt (PIL will add text perfectly)
    return (
        'hyperrealistic beautiful Indian devotional scene, '
        'golden hour sunlight, colorful Hindu temple in background, '
        'orange and yellow marigold flowers, green trees, '
        'a Krishna bansuri flute and two peacock feathers (morpankh) in foreground, '
        'warm vibrant saffron colors, cinematic DSLR photography, bokeh, '
        'NO people, NO text, NO watermark, NO Chinese, NOT a tomb, NOT dark'
    )


def generate_image_pollinations(path, retries=5):
    """Download background from Pollinations AI."""
    prompt = build_image_prompt()
    base_url = "https://image.pollinations.ai/prompt/"
    params = "?width=1080&height=1350&model=flux&nologo=true"
    for attempt in range(1, retries + 1):
        seed = random.randint(10000, 999999)
        url = base_url + requests.utils.quote(prompt, safe='') + params + f"&seed={seed}"
        print(f"Image attempt {attempt}/{retries}...")
        try:
            r = requests.get(url, timeout=120)
            ctype = r.headers.get("content-type", "")
            if r.status_code == 200 and "image" in ctype:
                img = Image.open(io.BytesIO(r.content))
                img.load()
                img.convert("RGB").save(path, "JPEG", quality=95)
                print(f"Background saved: {img.size}")
                return
            print(f"Bad response: {r.status_code}")
        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")
        time.sleep(8 * attempt)
    raise Exception("Image generation failed after all attempts.")


def add_text_overlay(image_path, thought, output_path):
    """Add Hindi thought text and PareshPadsala_ branding on the image using PIL."""
    print("Adding text overlay on image...")
    img = Image.open(image_path).convert("RGBA")
    W, H = img.size

    # Download Hindi font (Noto Sans Devanagari) if not present
    font_path = "NotoSansDevanagari.ttf"
    if not os.path.exists(font_path):
        font_url = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansDevanagari/NotoSansDevanagari-Bold.ttf"
        print("Downloading Hindi font...")
        r = requests.get(font_url, timeout=30)
        with open(font_path, "wb") as f:
            f.write(r.content)

    # ---- Dark semi-transparent banner in center ----
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    banner_h = int(H * 0.28)
    banner_y = int(H * 0.36)
    draw.rectangle([(0, banner_y), (W, banner_y + banner_h)], fill=(0, 0, 0, 160))

    # ---- Hindi Thought Text ----
    font_size = 68
    try:
        font = ImageFont.truetype(font_path, font_size)
        small_font = ImageFont.truetype(font_path, 36)
    except:
        font = ImageFont.load_default()
        small_font = font

    # Word wrap
    words = thought.split()
    lines, line = [], ""
    for word in words:
        test = line + word + " "
        if draw.textlength(test, font=font) < W - 80:
            line = test
        else:
            lines.append(line.strip())
            line = word + " "
    lines.append(line.strip())

    # Draw each line centered
    total_text_h = len(lines) * (font_size + 10)
    text_y = banner_y + (banner_h - total_text_h) // 2
    for line in lines:
        tw = draw.textlength(line, font=font)
        draw.text(((W - tw) // 2, text_y), line, font=font, fill=(255, 220, 100, 255))
        text_y += font_size + 10

    # ---- PareshPadsala_ at bottom ----
    brand = "@PareshPadsala_"
    bw = draw.textlength(brand, font=small_font)
    draw.text(((W - bw) // 2, H - 70), brand, font=small_font, fill=(255, 255, 255, 220))

    # Merge and save
    combined = Image.alpha_composite(img, overlay)
    combined.convert("RGB").save(output_path, "JPEG", quality=95)
    print("Text overlay added successfully!")

def instagram_login():
    print("Logging into Instagram via session...")
    session_data = json.loads(base64.b64decode(IG_SESSION).decode())
    sessionid = session_data.get("sessionid") or session_data.get("cookies", {}).get("sessionid", "")
    cl = Client()
    cl.login_by_sessionid(sessionid)
    print("Session loaded successfully!")
    return cl


def main():
    try:
        thought = generate_thought()
        raw_path = "background.jpg"
        generate_image_pollinations(raw_path)  # Step 1: Background
        add_text_overlay(raw_path, thought, IMAGE_PATH)  # Step 2: Add Hindi text

        caption = f"""{thought}

✨ Daily dose of inspiration and deep thoughts! ✨
Krishna ki bansuri aur morpankh ka ashirwad aapke sath rahe. 🦚🌸

Aise hi aur amazing thoughts aur premium posts ke liye hume jarur follow karein! 👇
👉 @PareshPadsala_

Like ❤️ | Comment 💬 | Share 🚀 | Save 📌

#trending #hindi #thoughts #krishna #flute #peacockfeather #dailyquotes #PareshPadsala_ #hindiquotes #suvichar #krishnalove #radhakrishna #motivationalquotes #hindithoughts #inspirationalquotes #deepthoughts"""

        cl = instagram_login()
        print("Uploading to Instagram...")
        cl.photo_upload(IMAGE_PATH, caption)
        print("Successfully Posted!")

    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)


if __name__ == "__main__":
    main()
