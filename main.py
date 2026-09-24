import os
import requests
import time
from instagrapi import Client
import google.generativeai as genai
from urllib.parse import quote

# Secrets from GitHub Actions
IG_USERNAME = os.environ.get("IG_USERNAME")
IG_PASSWORD = os.environ.get("IG_PASSWORD")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not all([IG_USERNAME, IG_PASSWORD, GEMINI_API_KEY]):
    print("Error: Please set IG_USERNAME, IG_PASSWORD, and GEMINI_API_KEY as environment variables.")
    exit(1)

genai.configure(api_key=GEMINI_API_KEY)

def generate_content():
    print("Generating a trending Hindi thought using Gemini...")
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # 1. Generate the Hindi quote
    prompt = "Write ONE deep, trending, and beautiful short Hindi thought/quote (max 10 words). Only return the Hindi text, nothing else."
    response = model.generate_content(prompt)
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
        
        # Upload to Instagram
        print("Logging into Instagram...")
        cl = Client()
        cl.login(IG_USERNAME, IG_PASSWORD)
        
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
