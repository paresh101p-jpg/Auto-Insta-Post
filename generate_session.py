"""
Instagram Session Generator - Browser Cookie Method
Ye method 100% reliable hai. Browser se sessionid copy karo.
"""
import json
import base64

print("=" * 55)
print("  Instagram Session Generator - Browser Cookie Method")
print("=" * 55)
print()
print("STEPS:")
print("1. Apne browser me Instagram.com kholo (already logged in hoga)")
print("2. F12 dabao (DevTools open hogi)")
print("3. 'Application' tab par click karo")
print("4. Left me 'Cookies' > 'https://www.instagram.com' par click karo")
print("5. 'sessionid' wali row dhundhoo")
print("6. Uski 'Value' column me jo lamba code hoga use copy karo")
print()
print("=" * 55)

sessionid = input("Yahan 'sessionid' ka value paste karo: ").strip()
username = input("Apna Instagram username: ").strip()

# Create session data with the sessionid cookie
session_data = {
    "sessionid": sessionid,
    "uuids": {
        "phone_id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
        "uuid": "aaaaaaaa-bbbb-cccc-dddd-ffffffffffff",
        "client_session_id": "aaaaaaaa-bbbb-cccc-dddd-aaaaaaaaaaaa",
        "advertising_id": "aaaaaaaa-bbbb-cccc-dddd-bbbbbbbbbbbb",
        "android_device_id": "android-aaaaaaaaaaaaaaaa"
    },
    "cookies": {"sessionid": sessionid},
    "last_login": 1700000000,
    "device_settings": {
        "app_version": "364.0.0.27.109",
        "android_version": 34,
        "android_release": "14.0",
        "dpi": "640dpi",
        "resolution": "1440x3200",
        "manufacturer": "samsung",
        "device": "SM-G998B",
        "model": "SM-G998B",
        "cpu": "qcom",
        "version_code": "617426896"
    },
    "user_agent": "Instagram 364.0.0.27.109 Android (34/14.0; 640dpi; 1440x3200; samsung; SM-G998B; SM-G998B; qcom; en_US; 617426896)"
}

session_json = json.dumps(session_data)
session_b64 = base64.b64encode(session_json.encode()).decode()

print()
print("=" * 55)
print("SUCCESS! Ab ye lamba code COPY karo:")
print("=" * 55)
print()
print(session_b64)
print()
print("=" * 55)
print("GitHub par jakar:")
print("Settings > Secrets > Actions > New secret")
print(f"Name: IG_SESSION")
print("Value: (upar wala lamba code paste karo)")
print("=" * 55)

# Save to file too
with open("instagram_session.txt", "w") as f:
    f.write(session_b64)
print("\nFile 'instagram_session.txt' me bhi save ho gayi!")
