"""
Run this script ONCE on your PC to generate Instagram session.
Then upload the session to GitHub Secrets.
"""
from instagrapi import Client
import json
import base64

print("=" * 50)
print("Instagram Session Generator")
print("=" * 50)
print()

username = input("Enter your Instagram username: ")
password = input("Enter your Instagram password: ")

cl = Client()

print("\nLogging in... (2FA code will be asked if needed)")

try:
    cl.login(username, password)
except Exception as e:
    if "two_factor" in str(e).lower() or "2fa" in str(e).lower() or "verification" in str(e).lower():
        code = input("\nEnter the 2FA code from your phone/email: ")
        cl.login(username, password, verification_code=code)
    else:
        raise e

# Save session
session_data = cl.get_settings()
session_json = json.dumps(session_data)
session_b64 = base64.b64encode(session_json.encode()).decode()

print("\n" + "=" * 50)
print("SUCCESS! Login ho gaya!")
print("=" * 50)
print("\nAb niche likha hua lamba code copy karo")
print("aur GitHub Secrets me 'IG_SESSION' naam se save karo:\n")
print(session_b64)
print("\n" + "=" * 50)
print("Copy the above code and save it in GitHub Secrets!")
print("=" * 50)

# Also save to file locally
with open("instagram_session.txt", "w") as f:
    f.write(session_b64)
print("\nSession file 'instagram_session.txt' me bhi save ho gayi hai.")
