import os
import requests
import time
from instagrapi import Client
from google import genai
from urllib.parse import quote

# Secrets from GitHub Actions
IG_USERNAME = os.environ.get("IG_USERNAME")
IG_SESSION = os.environ.get("IG_SESSION")  # Base64 encoded session
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not all([IG_USERNAME, IG_SESSION, GEMINI_API_KEY]):
    print("Error: Please set IG_USERNAME, IG_SESSION, and GEMINI_API_KEY as environment variables.")
    exit(1)

client = genai.Client(api_key=GEMINI_API_KEY)

def generate_content():
    print("Generating a trending Hindi thought using Gemini...")
    prompt = "Write ONE deep, trending, and beautiful short Hindi thought/quote (max 10 words). Only return the Hindi text, nothing else."
    # Try multiple models in order (fallback if one is busy)
    models_to_try = ['gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-3.6-flash']
    response = None
    for model_name in models_to_try:
        for attempt in range(3):  # Retry 3 times per model
            try:
                print(f"Trying model: {model_name} (attempt {attempt+1})...")
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                print(f"Success with model: {model_name}")
                break
            except Exception as e:
                print(f"Model {model_name} failed: {e}")
                time.sleep(5)  # Wait 5 sec before retry
        if response:
            break
    if not response:
        raise Exception("All Gemini models failed. Try again later.")

    hindi_thought = response.text.strip().replace('"', '')
    print(f"Today's thought: {hindi_thought}")
    
    # 2. Construct the Image Prompt as per user's strict requirement
    image_prompt = f'''Create a premium, ultra-realistic Instagram photograph. 
TEXT + LOCATION: "{hindi_thought}" — physically written/printed/painted on a beautiful ancient temple wall. 
Make the text look 100% REAL and physically present on the specified location, like a professionally photographed real-world mockup — never like a digital overlay, pasted PNG, sticker, floating text or Photoshop layer. 
Automatically adapt the typography to the exact surface. 
Create artistic typography with beautiful complementary colors. 
Include a beautiful Krishna flute (bansuri) and 2 peacock feathers (morpankh) beautifully placed in the composition. 
At the bottom center, the text "PareshPadsala_" must be written visibly and clearly. 
Ultra-realistic commercial photography, cinematic lighting, realistic materials, professional composition, HDR, sharp details, premium editorial look. vertical 9:16 aspect ratio.'''

    # 3. Use Pollinations AI (free text-to-image API which uses Flux)
    print("Generating Image...")
    # Pollinations creates images just by visiting the URL with the prompt
    encoded_prompt = quote(image_prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1920&nologo=true"
    
    return hindi_thought, image_url

def main():
    try:
        hindi_thought, img_url = generate_content()
        
        # Download Image
        print(f"Downloading image from: {img_url}")
        img_data = requests.get(img_url).content
        image_path = "today_post.jpg"
        with open(image_path, 'wb') as handler:
            handler.write(img_data)
            
        print("Image saved successfully.")
        
        # Login using saved session (no password/2FA needed)
        print("Logging into Instagram via session...")
        import json, base64
        cl = Client()
        session_data = json.loads(base64.b64decode(IG_SESSION).decode())
        cl.set_settings(session_data)
        cl.login(IG_USERNAME, "")  # Session auth - no password needed

        
        caption = f"""{hindi_thought}

✨ Daily dose of inspiration and deep thoughts! ✨
Krishna ki bansuri aur morpankh ka ashirwad aapke sath rahe. 🦚🌸

Aise hi aur amazing thoughts aur premium posts ke liye hume jarur follow karein! 👇
👉 @PareshPadsala_

Like ❤️ | Comment 💬 | Share 🚀 | Save 📌

#trending #hindi #thoughts #krishna #flute #peacockfeather #dailyquotes #PareshPadsala_ #hindiquotes #suvichar #krishnalove #radhakrishna #motivationalquotes #hindithoughts #inspirationalquotes #deepthoughts"""
        
        print("Uploading to Instagram...")
        cl.photo_upload(image_path, caption)
        print("Successfully Posted!")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)

if __name__ == "__main__":
    main()
