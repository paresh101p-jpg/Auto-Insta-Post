import os
import io
import json
import time
import base64
import random
import requests
from PIL import Image
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


def build_image_prompt(thought):
    # Very specific Indian devotional scene - avoids Chinese/tomb/monument style
    return (
        f'hyperrealistic Instagram photo, beautiful Indian Hindu temple scene, '
        f'golden hour sunlight, orange marigold flowers everywhere, '
        f'a wooden signboard in the scene with Hindi text "{thought}" painted on it in saffron color, '
        f'a Krishna bansuri flute lying on the ground, '
        f'two colorful peacock feathers (morpankh) placed next to the flute, '
        f'small text PareshPadsala written at bottom, '
        f'warm vibrant colors, cinematic photography, bokeh background, '
        f'NOT a tomb, NOT a monument, NOT Chinese, NOT Japanese, NOT dark, '
        f'beautiful devotional Indian aesthetic'
    )


def generate_image_pollinations(prompt, path, retries=5):
    """Download from Pollinations AI - free image generation."""
    base_url = "https://image.pollinations.ai/prompt/"
    params = f"?width=1080&height=1350&model=flux&nologo=true"
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
                print(f"Image saved: {img.size}")
                return
            print(f"Bad response: {r.status_code}, {ctype}")
        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")
        time.sleep(8 * attempt)
    raise Exception("Image generation failed after all attempts.")



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
        generate_image_pollinations(build_image_prompt(thought), IMAGE_PATH)

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
