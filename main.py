import os
import json
import time
import base64
import subprocess
from instagrapi import Client
from google import genai
from PIL import Image

# Secrets from GitHub Actions
IG_USERNAME = os.environ.get("IG_USERNAME")
IG_SESSION  = os.environ.get("IG_SESSION")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not all([IG_USERNAME, IG_SESSION, GEMINI_API_KEY]):
    print("Error: Please set IG_USERNAME, IG_SESSION, and GEMINI_API_KEY.")
    exit(1)

client = genai.Client(api_key=GEMINI_API_KEY)
IMAGES_FOLDER = "images"
GEMINI_MODELS  = ["gemini-3.6-flash"]


def get_next_image():
    """Pick the first available image from the images/ folder."""
    if not os.path.exists(IMAGES_FOLDER):
        raise Exception(f"'{IMAGES_FOLDER}' folder not found! Upload images there first.")
    files = sorted([
        f for f in os.listdir(IMAGES_FOLDER)
        if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
    ])
    if not files:
        raise Exception("No images left in 'images/' folder! Please upload more images.")
    chosen = os.path.join(IMAGES_FOLDER, files[0])
    print(f"Using image: {chosen} ({len(files)} remaining)")
    return chosen


def generate_caption(image_path):
    """Read the exact Hindi thought written ON the image using Gemini Vision."""
    print("Reading Hindi text from the image using Gemini Vision...")
    prompt = (
        "Read the Hindi text written on this image. "
        "Return ONLY the exact Hindi text you see in the image, nothing else. "
        "Do not add any quotes or extra words."
    )
    
    img = Image.open(image_path)
    
    for model_name in GEMINI_MODELS:
        for attempt in range(1, 6):
            try:
                print(f"Trying {model_name} (attempt {attempt})...")
                resp = client.models.generate_content(
                    model=model_name, 
                    contents=[img, prompt]
                )
                text = resp.text.strip().replace('"', '')
                if text:
                    print(f"Extracted Caption: {text}")
                    return text
            except Exception as e:
                print(f"Failed: {e}")
                time.sleep(5 * attempt)
    return "कृष्णा की बांसुरी और मोरपंख का आशीर्वाद आपके साथ रहे।"  # fallback


def delete_posted_image(image_path):
    """Delete the posted image and commit the change to GitHub."""
    print(f"Deleting posted image: {image_path}")
    os.remove(image_path)
    try:
        subprocess.run(["git", "config", "user.email", "bot@autopost.com"], check=True)
        subprocess.run(["git", "config", "user.name", "Auto Post Bot"], check=True)
        subprocess.run(["git", "add", "-A"], check=True)
        subprocess.run(["git", "commit", "-m", f"Posted and removed: {os.path.basename(image_path)}"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("Image deleted and pushed to GitHub!")
    except Exception as e:
        print(f"Git push warning: {e}")


def instagram_login():
    print("Logging into Instagram via session...")
    session_data = json.loads(base64.b64decode(IG_SESSION).decode())
    sessionid = (session_data.get("sessionid")
                 or session_data.get("cookies", {}).get("sessionid", ""))
    cl = Client()
    cl.login_by_sessionid(sessionid)
    print("Logged in successfully!")
    return cl


def main():
    try:
        # Step 1: Get next image from folder
        image_path = get_next_image()

        # Step 2: Extract caption from the image itself
        thought = generate_caption(image_path)

        # Step 3: Build Instagram caption
        caption = f"""{thought}

✨ Daily dose of inspiration and deep thoughts! ✨
Krishna ki bansuri aur morpankh ka ashirwad aapke sath rahe. 🦚🌸

Aise hi aur amazing thoughts ke liye follow karein! 👇
👉 @PareshPadsala_

Like ❤️ | Comment 💬 | Share 🚀 | Save 📌

#trending #hindi #thoughts #krishna #flute #peacockfeather #dailyquotes #PareshPadsala_ #hindiquotes #suvichar #krishnalove #radhakrishna #motivationalquotes #hindithoughts #inspirationalquotes #deepthoughts"""

        # Step 4: Post to Instagram
        cl = instagram_login()
        print("Uploading to Instagram...")
        cl.photo_upload(image_path, caption)
        print("Successfully Posted! ✅")

        # Step 5: Delete posted image so it never repeats
        delete_posted_image(image_path)

    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)


if __name__ == "__main__":
    main()
