import os
import io
import json
import time
import base64
import random
import requests
from urllib.parse import quote
from PIL import Image
from instagrapi import Client
from google import genai

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
    return (
        f'A stunning premium Instagram photo in vertical format. '
        f'A beautiful Indian woman in traditional attire sitting near a colorful temple, '
        f'holding a Krishna bansuri flute, with 2 vibrant peacock feathers (morpankh) placed elegantly nearby. '
        f'Warm golden hour lighting, marigold flowers, soft bokeh background. '
        f'In the center of the image, the Hindi text "{thought}" is written in large, '
        f'beautiful calligraphy style on a wooden board or stone slab in the scene. '
        f'At the bottom of the image, small elegant text reads "PareshPadsala_". '
        f'Ultra-realistic DSLR photography, vibrant colors, cinematic composition, '
        f'NO Chinese symbols, NO tomb, NO monument, NO Japanese text. '
        f'Indian temple aesthetic, devotional mood, premium editorial look.'
    )


def download_image(prompt, path, retries=5):
    """Download from Pollinations, VERIFY it is a real image, save as JPEG."""
    encoded = quote(prompt, safe="")
    for attempt in range(1, retries + 1):
        seed = random.randint(1, 999999)
        url = (f"https://image.pollinations.ai/prompt/{encoded}"
               f"?width={IMG_WIDTH}&height={IMG_HEIGHT}&model=flux&nologo=true&seed={seed}")
        print(f"Image attempt {attempt}/{retries} (URL length: {len(url)})...")
        try:
            r = requests.get(url, timeout=180)
            ctype = r.headers.get("content-type", "")
            if r.status_code == 200 and ctype.startswith("image"):
                img = Image.open(io.BytesIO(r.content))
                img.load()  # raises if the data is corrupt
                img.convert("RGB").save(path, "JPEG", quality=95)
                print(f"Image saved: {img.size}")
                return
            # This line shows the REAL reason if Pollinations refuses
            print(f"Bad response: status={r.status_code}, type={ctype}, body={r.text[:300]!r}")
        except Exception as e:
            print(f"Image download failed: {e}")
        time.sleep(10 * attempt)
    raise Exception("Could not get a valid image from Pollinations.")


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
        download_image(build_image_prompt(thought), IMAGE_PATH)

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
