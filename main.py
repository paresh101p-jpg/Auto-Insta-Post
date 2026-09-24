import os
import time
import subprocess
import requests
from google import genai
from PIL import Image

# Secrets from GitHub Actions
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
FB_PAGE_ID = os.environ.get("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.environ.get("FB_ACCESS_TOKEN")

if not all([GEMINI_API_KEY, FB_PAGE_ID, FB_ACCESS_TOKEN]):
    print("Error: Please set GEMINI_API_KEY, FB_PAGE_ID, and FB_ACCESS_TOKEN in GitHub Secrets.")
    exit(1)

client = genai.Client(api_key=GEMINI_API_KEY)
IMAGES_FOLDER = "images"
GEMINI_MODELS  = ["gemini-1.5-flash", "gemini-1.5-pro"]
GITHUB_REPO_RAW_URL = "https://raw.githubusercontent.com/paresh101p-jpg/Auto-Insta-Post/main/"

def get_next_image():
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
    print("Reading Hindi text from the image using Gemini Vision...")
    prompt = (
        "You are an expert Instagram Social Media Manager. Look at the image provided. "
        "First, extract the exact Hindi text written on the image. "
        "Then, write a long, engaging Instagram caption in a mix of Hindi and English (Hinglish) based on that text. "
        "Your response MUST be the final Instagram caption, formatted beautifully with emojis. "
        "Include the following elements in this exact order:\n"
        "1. The exact Hindi text from the image at the very top.\n"
        "2. A 3-4 line beautiful and deep explanation or thought inspired by the text in Hinglish.\n"
        "3. A call to action exactly like this:\n\n"
        "Aise hi aur amazing thoughts ke liye follow karein! 👇\n"
        "👉 @pareshpadsala_\n\n"
        "Like ❤️ | Comment 💬 | Share 🚀 | Save 📌\n\n"
        "4. At least 15-20 highly relevant hashtags at the bottom (e.g., #hindi #quotes #suvichar #PareshPadsala_ etc.). "
        "Do not include any extra text outside the caption itself."
    )
    img = Image.open(image_path)
    
    for model_name in GEMINI_MODELS:
        for attempt in range(1, 4):
            try:
                print(f"Trying {model_name} (attempt {attempt})...")
                resp = client.models.generate_content(
                    model=model_name, 
                    contents=[img, prompt]
                )
                text = resp.text.strip()
                if text:
                    print(f"Extracted Caption Generated!\n")
                    return text
            except Exception as e:
                print(f"Failed: {e}")
                time.sleep(5 * attempt)
    
    return """कृष्णा की बांसुरी और मोरपंख का आशीर्वाद आपके साथ रहे। 🦚🌸\n\nZindagi me shanti aur prem hamesha bana rahe!\n\nAise hi aur amazing thoughts ke liye follow karein! 👇\n👉 @pareshpadsala_\n\nLike ❤️ | Comment 💬 | Share 🚀 | Save 📌\n\n#hindi #thoughts #krishna #dailyquotes #pareshpadsala_ #hindiquotes #suvichar #motivationalquotes"""

def get_ig_account_id():
    print("Fetching connected Instagram Account ID...")
    url = f"https://graph.facebook.com/v20.0/{FB_PAGE_ID}?fields=instagram_business_account&access_token={FB_ACCESS_TOKEN}"
    res = requests.get(url).json()
    ig_id = res.get('instagram_business_account', {}).get('id')
    if ig_id:
        print(f"Found IG Account ID: {ig_id}")
    else:
        print("Warning: No Instagram Business Account linked to this Facebook Page.")
    return ig_id

def post_fb_feed(caption, image_url):
    print("Posting to Facebook Feed...")
    fb_caption = caption.replace("@pareshpadsala_", "@Krishna Vibez")
    url = f"https://graph.facebook.com/v20.0/{FB_PAGE_ID}/photos"
    payload = {'message': fb_caption, 'url': image_url, 'access_token': FB_ACCESS_TOKEN}
    res = requests.post(url, data=payload).json()
    if 'id' in res:
        print(f"✅ FB Feed Success (ID: {res['id']})")
    else:
        print(f"❌ FB Feed Failed: {res}")

def post_fb_story(image_url):
    print("Posting to Facebook Story...")
    url = f"https://graph.facebook.com/v20.0/{FB_PAGE_ID}/photo_stories"
    payload = {'url': image_url, 'access_token': FB_ACCESS_TOKEN}
    res = requests.post(url, data=payload).json()
    if 'id' in res:
        print(f"✅ FB Story Success (ID: {res['id']})")
    else:
        print(f"❌ FB Story Failed: {res}")

def post_ig_media(ig_account_id, caption, image_url, is_story=False):
    target = "Story" if is_story else "Feed"
    print(f"Posting to Instagram {target}...")
    
    # Step 1: Create Container
    url = f"https://graph.facebook.com/v20.0/{ig_account_id}/media"
    payload = {'image_url': image_url, 'access_token': FB_ACCESS_TOKEN}
    if is_story:
        payload['media_type'] = 'STORIES'
    else:
        payload['caption'] = caption
        
    res = requests.post(url, data=payload).json()
    creation_id = res.get('id')
    
    if not creation_id:
        print(f"❌ IG Container Creation Failed for {target}: {res}")
        return
        
    # Step 2: Publish Container
    print(f"Publishing IG {target} container...")
    pub_url = f"https://graph.facebook.com/v20.0/{ig_account_id}/media_publish"
    pub_payload = {'creation_id': creation_id, 'access_token': FB_ACCESS_TOKEN}
    
    # Wait a few seconds for IG to process the image container
    time.sleep(5)
    
    for attempt in range(3):
        pub_res = requests.post(pub_url, data=pub_payload).json()
        if 'id' in pub_res:
            print(f"✅ IG {target} Success (ID: {pub_res['id']})")
            return
        elif pub_res.get('error', {}).get('code') == 9007:
            # Media not ready, wait and retry
            print(f"Media not ready, retrying... (Attempt {attempt+1})")
            time.sleep(5)
        else:
            print(f"❌ IG Publish Failed for {target}: {pub_res}")
            return

def delete_posted_image(image_path):
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

def main():
    try:
        # Step 1: Get next image from folder
        image_path = get_next_image()
        
        # Step 2: Convert local path to GitHub Raw URL
        # e.g. "images/123.jpg" -> "https://raw.github.../images/123.jpg"
        clean_path = image_path.replace("\\", "/")
        public_image_url = GITHUB_REPO_RAW_URL + clean_path
        print(f"Generated Public URL: {public_image_url}")

        # Step 3: Extract and generate full caption using Gemini
        caption = generate_caption(image_path)

        # Step 4: Post to Facebook Feed
        post_fb_feed(caption, public_image_url)
        
        # Step 5: Post to Facebook Story
        post_fb_story(public_image_url)

        # Step 6 & 7: Instagram Posting (If linked)
        ig_account_id = get_ig_account_id()
        if ig_account_id:
            # Post to IG Feed
            post_ig_media(ig_account_id, caption, public_image_url, is_story=False)
            # Post to IG Story
            post_ig_media(ig_account_id, "", public_image_url, is_story=True)

        # Step 8: Delete posted image so it never repeats
        delete_posted_image(image_path)

    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)

if __name__ == "__main__":
    main()
