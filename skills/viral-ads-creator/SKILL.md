---
name: viral-ads-creator
description: Research trending social media videos/memes and transform them into viral ads for Clean Up Bros. Use when a user wants to create attractive, trending image or video advertisements for Liverpool and surrounding areas. This skill identifies viral trends, adapts them to cleaning services, generates high-CTR captions, and coordinates image/video generation via Nano Banana Pro or Kie AI.
---

# Viral Ads Creator

This skill automates the process of identifying global and local (Sydney/Liverpool) viral trends and adapting them to market **Clean Up Bros**.

## Workflow

1. **Trend Spotting**: Use `web_search` to find the most viral memes, video formats (TikTok/IG Reels), or trending news in the cleaning industry and general pop culture for the current date.
2. **Clean Up Bros Adaptation**: Pivot the trend to a cleaning context.
   - Example: If a "Day in the life" of a corporate worker is trending, create a "Day in the life of a Clean Up Bro making a Liverpool home shine."
3. **Asset Generation**:
   - **Images**: Use **Nano Banana Pro** (Gemini 3 Pro Image) for high-quality, realistic images of cleaning transformations or brand mascots.
   - **Videos**: Use **Kie AI** or similar for generating short viral-style video clips.
4. **Copywriting**: Generate high-CTR captions focused on **Liverpool, NSW** and surrounding areas.
   - Tone: Professional, local, energetic.
   - CTA: "DM for a quote", "Book your spring clean", "Liverpool's #1 Cleaners".

## References

- See `references/targeting.md` for specific Liverpool/Greater Sydney location insights.
- See `references/trending-logs.md` for a log of previously used trends to avoid repetition.

## Scripts

- `scripts/research_trends.py`: (Optional) Automates the search for viral tags and formats.

## Assets

- `assets/logo.png`: Brand assets for Clean Up Bros.
