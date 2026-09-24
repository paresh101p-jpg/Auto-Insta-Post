# Auto Instagram & Facebook Post - Project Notes

## Project Overview
Ye ek automated Social Media posting bot hai jo roz apne aap:
1. Gemini AI se ek naya **Hindi thought/quote** padhta hai image par se.
2. Us image ko **Facebook Page (Krishna Vibez)** aur **Instagram (@pareshpadsala_)** dono jagah automatically post karta hai (Feed + Story).
3. Post hone ke baad image ko GitHub repository se delete kar deta hai.

**GitHub Repo:** `github.com/paresh101p-jpg/Auto-Insta-Post`  
**Post Time:** Roz **3:30 PM IST** (10:00 AM UTC) - GitHub Actions se automatic

---

## Architecture (NEW META GRAPH API METHOD)
Ab humne purana `instagrapi` library aur 90-din wala session method hata diya hai. Ab bot directly **Meta Graph API** ka use karta hai!

### Kaise Kaam Karta Hai?
1. **GitHub Raw URL Trick:** API ko upload ke liye public link chahiye hota hai. Humare images public GitHub repo me hain, toh bot direct GitHub Raw URL (`https://raw.githubusercontent.com/...`) banata hai. Isse humein Catbox ya kisi 3rd party host ki zarurat nahi padti.
2. **Facebook Post:** Bot permanent token ka use karke Facebook Feed aur Story par public link bhej kar post lagata hai.
3. **Instagram Post:** Bot Facebook page se linked Instagram Business Account ka ID nikalta hai, aur us id par Instagram Feed aur Story post karta hai.
4. **Delete Logic:** Jab chaaron jagah (FB Feed, IG Feed, FB Story, IG Story) success ho jati hai ya attempt ho jata hai, aakhir me bot `images/` folder se image delete kar ke GitHub me commit kar deta hai.

---

## File Structure
```
Auto-Insta-Post/
├── main.py                  → Main bot script (API logic yahi hai)
├── requirements.txt         → Python libraries (requests, google-genai, pillow)
├── images/                  → Yaha par sabhi photos upload karni hoti hain
├── fb_permanent_token.txt   → Facebook ka Never-Expiring token backup
└── .github/
    └── workflows/
        └── schedule.yml     → GitHub Actions schedule (roz 3:30 PM IST)
```

---

## GitHub Secrets (Settings > Secrets > Actions)
Aapko bas ye secrets set rakhne hain:

| Secret Name | Value |
|-------------|-------|
| `FB_PAGE_ID` | `1808917602588221` |
| `FB_ACCESS_TOKEN` | (fb_permanent_token.txt me jo bada sa token hai wo dale) |
| `GEMINI_API_KEY` | (Google Gemini API key) |

> ⚠️ `IG_USERNAME`, `IG_SESSION`, aur `IG_PASSWORD` ab zarurat nahi hain, inko delete kar sakte hain.

---

## Errors Aur Unke Solutions

| Error | Cause | Fix |
|-------|-------|-----|
| `404 NOT_FOUND` (gemini) | Model band ho gaya | `GEMINI_MODELS` list me naya model naam daalo |
| `503 UNAVAILABLE` | Gemini server busy | Retry logic automatic hai, thoda wait karo |
| `Graph API Error` | Token expire / revoke | Naya token generate karke GitHub secrets me dale |
| `No images left` | Folder khali ho gaya | GitHub pe `images/` folder me nayi photos upload karein |

---

## Post Caption Format
```
[Hindi Thought - Gemini dwara image se extract kiya hua]

✨ Daily dose of inspiration and deep thoughts! ✨
Krishna ki bansuri aur morpankh ka ashirwad aapke sath rahe. 🦚🌸

Aise hi aur amazing thoughts aur premium posts ke liye hume jarur follow karein! 👇
👉 @pareshpadsala_  (Ya FB par @Krishna Vibez)

Like ❤️ | Comment 💬 | Share 🚀 | Save 📌

#trending #hindi #thoughts #krishna #flute #peacockfeather #dailyquotes ...
```

---

## Future Roadmap (Threads Auto-Post)
- Agla step **Threads (.threads.net)** par bhi auto-post lagana hai.
- **Requirement:** Meta for Developers me ek naya token generate karna padega jisme `threads_content_publish` aur `threads_basic` ki permission tick ho.
- **Note:** Threads API bhi completely FREE hai! Ek baar IG+FB ka test stable ho jaye, fir ise bhi add kar denge.

---

*Last Updated: September 24, 2026*
