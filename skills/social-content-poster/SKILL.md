---
name: social-content-poster
description: Research trending content, create viral posts, and publish to Facebook & Instagram for Clean Up Bros. Use when asked to post on social media, create content for Clean Up Bros, grow the cleaning business social presence, or schedule social media posts. Triggers on "post to Instagram", "Facebook post", "social media", "viral content", "grow Clean Up Bros".
---

# Social Content Poster

Automated social media content creation and posting for **Clean Up Bros** (Sydney cleaning business).

## Quick Start

1. Research trending content via Perplexity or web_search
2. Adapt trend to cleaning context
3. Generate image/video asset
4. Write high-engagement caption
5. Post to Facebook + Instagram
6. Log post to avoid repetition

## Brand Details

- **Business:** Clean Up Bros
- **Services:** End-of-lease, Airbnb turnovers, NDIS cleaning, general cleans, commercial
- **Location:** Liverpool, Sydney & surrounding areas (Western Sydney)
- **Tone:** Professional, local, energetic, relatable
- **Target:** Homeowners, renters, Airbnb hosts, property managers, NDIS participants

## Content Research Workflow

### Step 1: Find Trending Content

Use Perplexity (browser) or web_search:

```
trending viral cleaning business reels Instagram Facebook [current month] [current year]
```

Also search:
- TikTok cleaning trends
- Satisfying cleaning videos viral
- Before after transformation trends
- Sydney local news/events (for timely content)

### Step 2: Check Post History

Read `references/post-log.md` to avoid repeating recent content.

### Step 3: Adapt to Clean Up Bros

Transform the trend:
- Generic cleaning → Liverpool/Sydney specific
- Influencer style → Small business authenticity
- Add local references (suburbs, landmarks, weather)

## Content Types (Rotation)

Post variety throughout the week:

| Day | Content Type | Example |
|-----|--------------|---------|
| Mon | Before/After Transformation | End-of-lease reveal |
| Tue | Quick Cleaning Hack | "Hard water trick" |
| Wed | Poll/Engagement Post | "Worst chore to clean?" |
| Thu | Airbnb/Commercial Showcase | Turnover timelapse |
| Fri | POV/Relatable Reel | "POV: You hired cleaners" |
| Sat | Customer Review/Testimonial | Screenshot + thank you |
| Sun | Behind the Scenes | Day in the life |

## Image Generation

Use **Nano Banana Pro** skill for images:

```
Generate a before/after cleaning transformation image. Left side: messy kitchen with dirty dishes, grease on stovetop. Right side: same kitchen sparkling clean, organized. Bright lighting, realistic photo style. Text overlay space at top.
```

For logos/branding, use `assets/logo.png`.

## Caption Formula

### High-Engagement Structure

```
[HOOK - 1 line that stops scroll]

[STORY/VALUE - 2-3 lines]

[CTA - Clear action]

[HASHTAGS - 5-10 relevant]
```

### Example Captions

**Transformation Post:**
```
This kitchen hadn't been cleaned in 6 months. 😱

3 hours later → spotless and ready for inspection.
Bond? ✅ Returned in full.

Liverpool & Western Sydney 📍 DM "CLEAN" for a free quote!

#endofleasecleaning #sydneycleaning #bondcleaning #cleanupbros #liverpoolnsw #beforeandafter #cleaningmotivation #propertycleaning
```

**Engagement Post:**
```
Be honest... which one do you HATE cleaning the most? 👇

A) Oven 🔥
B) Shower glass 🚿
C) Toilet 🚽

Comment below and we might just do it FREE on your next booking! 😉

#cleaningpoll #sydneycleaners #cleanupbros #cleaninghacks
```

**POV Reel:**
```
POV: You finally stopped doing it yourself and hired the pros 💅

Your weekends are yours again.
Your bond comes back in full.
Your Airbnb gets 5-star reviews.

This could be you → Link in bio 🔗

#cleaningservice #liverpoolcleaning #airbnbcleaning #cleanupbros #povreels
```

## Posting Procedure

### Facebook Page Post

1. Open browser to Facebook Business Suite or facebook.com
2. Navigate to Clean Up Bros page
3. Click "Create Post"
4. Upload image/video
5. Paste caption
6. Add location tag: Liverpool, NSW (or job suburb)
7. Post immediately or schedule

### Instagram Post

1. Open browser to Instagram or Business Suite
2. Click "+" to create post
3. Upload image/video
4. Paste caption (Instagram version - shorter)
5. Add location tag
6. Add alt text for accessibility
7. Post or schedule

### Cross-Posting

If accounts are linked via Meta Business Suite:
1. Create post once
2. Toggle both Facebook + Instagram
3. Publish to both simultaneously

## Posting Schedule

**Optimal times (Sydney/AEST):**
- Morning: 7:00-8:00 AM
- Lunch: 12:00-1:00 PM  
- Evening: 7:00-9:00 PM

**Frequency:** 1-3 posts per day

## After Posting

1. Log post to `references/post-log.md`:
   ```
   ## 2026-02-16
   - Platform: Instagram + Facebook
   - Type: Before/After
   - Caption: [first line]
   - Engagement: [update after 24hrs]
   ```

2. Monitor comments for 1 hour after posting
3. Reply to comments quickly (boosts algorithm)
4. Save high-performing posts to replicate format

## Hashtag Bank

### Primary (always use 3-5):
#cleanupbros #sydneycleaning #liverpoolnsw #westernsydney #cleaningservice

### Content-Specific:
- Transformations: #beforeandafter #cleaningtransformation #satisfyingcleaning
- End of lease: #endofleasecleaning #bondcleaning #bondback #movingout
- Airbnb: #airbnbcleaning #airbnbhost #shorttermrental #turnoverday
- NDIS: #ndiscleaning #ndissupport #disabilitysupport
- Commercial: #commercialcleaning #officecleaning #retailcleaning

### Trending (rotate):
#cleaningtiktok #cleaningmotivation #cleantok #satisfying #asmrcleaning

## Emergency Content

If no time for research, use these reliable formats:

1. **Repost transformation** from camera roll with new caption
2. **Quick tip** text post (no image needed)
3. **Story poll** "Coffee or tea while we clean your place? ☕🍵"
4. **Quote graphic** "A clean home is a happy home"

## Connected Accounts

**Facebook Page:** CLEAN UP BROS (ID: 707617919097782)
**Instagram:** Linked (ID: 17841475542958087)

API credentials in `~/.clawdbot/.env`:
- `META_SYSTEM_USER_TOKEN`
- `META_BUSINESS_ID`

## API Posting Commands

```bash
# List accounts
python3 scripts/post_to_meta.py list

# Post text only to Facebook
python3 scripts/post_to_meta.py post "Your caption here"

# Post image to both Facebook + Instagram
python3 scripts/post_to_meta.py post "Your caption" --image https://url-to-image.jpg

# Post Reel to Instagram
python3 scripts/post_to_meta.py reel "Your caption" --video https://url-to-video.mp4
```

**Note:** Instagram requires PUBLIC image/video URLs. Upload to a hosting service first if needed.

## Files

- `references/post-log.md` — History of posts
- `references/caption-templates.md` — Reusable captions
- `references/hashtags.md` — Full hashtag library
- `assets/logo.png` — Clean Up Bros logo
- `assets/templates/` — Canva/image templates
