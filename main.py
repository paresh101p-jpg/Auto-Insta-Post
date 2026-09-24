import os
import io
import json
import time
import base64
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
    return (
        f'A stunning premium Instagram photograph in vertical 4:5 format. '
        f'A beautiful Indian woman in traditional saree sitting near a vibrant colorful temple. '
        f'She is holding a Krishna bansuri flute. '
        f'Two beautiful peacock feathers (morpankh) placed elegantly nearby with marigold flowers. '
        f'In the center, a decorative wooden board with the Hindi Devanagari text "{thought}" '
        f'written in beautiful calligraphy. '
        f'At the very bottom center, elegant small text reads "PareshPadsala_". '
        f'Golden hour lighting, soft bokeh, ultra-realistic DSLR photography, '
        f'vibrant Indian colors, cinematic premium editorial quality. '
        f'Devotional Krishna aesthetic. No watermarks.'
    )


def generate_image_gemini(prompt, path):
    """Generate image using Gemini flash image generation (free Developer API)."""
    print("Generating image using Gemini Flash Image Generation...")
    for attempt in range(1, 4):
        try:
            print(f"Image generation attempt {attempt}/3...")
            response = client.models.generate_content(
                model="gemini-2.0-flash-exp-image-generation",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["Text", "Image"]
                )
            )
            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    image_bytes = part.inline_data.data
                    img = Image.open(io.BytesIO(image_bytes))
                    img.convert("RGB").save(path, "JPEG", quality=95)
                    print(f"Image saved successfully: {img.size}")
                    return
            print("No image found in response, retrying...")
        except Exception as e:
            print(f"Imagen attempt {attempt} failed: {e}")
            time.sleep(10 * attempt)
    raise Exception("Gemini image generation failed after 3 attempts.")



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
        generate_image_gemini(build_image_prompt(thought), IMAGE_PATH)

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
