# Auto Instagram Post - Project Notes

## Project Overview
Ye ek automated Instagram posting bot hai jo roz apne aap:
1. Gemini AI se ek naya **Hindi thought/quote** generate karta hai
2. **Pollinations AI** (free) se ek ultra-realistic image banata hai (Bansuri + Morpankh + PareshPadsala_)
3. Us image ko **@pareshpadsala_** Instagram account par automatically post karta hai

**GitHub Repo:** `github.com/paresh101p-jpg/Auto-Insta-Post`  
**Post Time:** Roz **3:30 PM IST** (10:00 AM UTC) - GitHub Actions se automatic

---

## File Structure
```
Auto-Insta-Post/
├── main.py                  → Main bot script
├── generate_session.py      → Ek baar chalao - Instagram session banane ke liye
├── requirements.txt         → Python libraries
├── instagram_session.txt    → Generated session (DO NOT SHARE!)
└── .github/
    └── workflows/
        └── schedule.yml     → GitHub Actions schedule (roz 3:30 PM IST)
```

---

## GitHub Secrets (Settings > Secrets > Actions)
| Secret Name | Value |
|-------------|-------|
| `IG_USERNAME` | pareshpadsala_ |
| `IG_SESSION` | (base64 encoded session - from instagram_session.txt) |
| `GEMINI_API_KEY` | (Google Gemini API key) |

> ⚠️ `IG_PASSWORD` secret delete kar do - ab zarurat nahi

---

## How It Works (Technical)
1. **Gemini API** (`gemini-3.6-flash` model) → Hindi thought generate karta hai
2. **Pollinations AI** (`image.pollinations.ai`) → Free image generation (1080x1350 px)
3. **instagrapi** library → `login_by_sessionid()` se Instagram me login karke post karta hai

---

## Session Refresh (Har 90 din baad)
Jab GitHub Actions me post fail ho (session expire), tab ye karo:

### Step 1 - Session dubara generate karo
```bash
cd "D:\Online\DTF STICKER LISTING\Auto-Insta-Post"
python generate_session.py
```
- Browser me Instagram.com kholo → F12 → Application → Cookies → `sessionid` value copy karo
- Script me paste karo → naya lamba code milega

### Step 2 - GitHub Secret update karo
- GitHub → Repo → Settings → Secrets → `IG_SESSION` → Update
- Naya code paste karo → Save

### Step 3 - Bot wapas chalu! ✅

---

## Errors Aur Unke Solutions

| Error | Cause | Fix |
|-------|-------|-----|
| `404 NOT_FOUND` (gemini model) | Model band ho gaya | `GEMINI_MODELS` list me naya model naam daalo |
| `503 UNAVAILABLE` | Gemini server busy | Retry logic automatic hai, thoda wait karo |
| `IG_SESSION not set` | Workflow YAML me secret missing | `schedule.yml` me `IG_SESSION` check karo |
| `Session expired` | 90 din ho gaye | Upar wala "Session Refresh" process karo |
| Instagram login failed | Session invalid | Browser se naya sessionid lo |

---

## Post Caption Format
```
[Hindi Thought]

✨ Daily dose of inspiration and deep thoughts! ✨
Krishna ki bansuri aur morpankh ka ashirwad aapke sath rahe. 🦚🌸

Aise hi aur amazing thoughts aur premium posts ke liye hume jarur follow karein! 👇
👉 @PareshPadsala_

Like ❤️ | Comment 💬 | Share 🚀 | Save 📌

#trending #hindi #thoughts #krishna #flute #peacockfeather #dailyquotes #PareshPadsala_ 
#hindiquotes #suvichar #krishnalove #radhakrishna #motivationalquotes #hindithoughts 
#inspirationalquotes #deepthoughts
```

---

## Image Details
- **Size:** 1080 x 1350 px (4:5 ratio - Instagram feed ke liye best)
- **Elements:** Hindi text + Bansuri + 2 Morpankh + "PareshPadsala_" at bottom
- **Style:** Ultra-realistic, ancient temple wall, cinematic lighting, HDR

---

## Manual Test Karna Ho To
GitHub → `Auto-Insta-Post` repo → **Actions** tab → **"Auto Instagram Post"** → **"Run workflow"** button

---

*Last Updated: September 24, 2026*
