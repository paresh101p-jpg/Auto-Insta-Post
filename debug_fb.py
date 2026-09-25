import requests

TOKEN = open("fb_permanent_token.txt").read().strip()

print("=" * 60)
print("STEP 1: Token ke saath konsi PAGES hain?")
print("=" * 60)
url = f"https://graph.facebook.com/v20.0/me/accounts?access_token={TOKEN}"
res = requests.get(url).json()
print(res)

if "data" in res and res["data"]:
    print("\n✅ Ye pages available hain is token pe:")
    for page in res["data"]:
        print(f"  Page Name: {page.get('name')}")
        print(f"  Page ID:   {page.get('id')}")
        print(f"  Token:     {page.get('access_token', 'N/A')[:30]}...")
        print()
else:
    print("\n❌ Koi page nahi mila ya token invalid hai!")

print("=" * 60)
print("STEP 2: Token ka debug info")
print("=" * 60)
debug_url = f"https://graph.facebook.com/debug_token?input_token={TOKEN}&access_token={TOKEN}"
debug_res = requests.get(debug_url).json()
data = debug_res.get("data", {})
print(f"App ID: {data.get('app_id')}")
print(f"Type:   {data.get('type')}")
print(f"Valid:  {data.get('is_valid')}")
print(f"Expires: {data.get('expires_at', 'Never (permanent)')}")
print(f"Scopes: {data.get('scopes', [])}")
