# 2026-02-02 - Gemini API Quota Fix

## Issue
Bella (Telegram bot @CubsBookKeeperBot) was returning quota exhausted errors:
```
LLM error: {"error": {"code": 429, "message": "You exceeded your current quota...", "status": "RESOURCE_EXHAUSTED"}}
```

## Root Cause
The Gemini API key in `~/.clawdbot/.env` had hit its daily free tier rate limit:
- 15 requests per minute (RPM)
- 1 million tokens per minute (TPM)
- 1,500 requests per day (RPD)

## Resolution
1. Tested new Gemini API key (provided by Hafsah)
2. Updated `~/.clawdbot/.env` with new key:
   - GOOGLE_API_KEY=AIzaSyDan3cu5TNfaYiQz7jQUbmrhzajXLLxD48
   - GEMINI_API_KEY=AIzaSyDan3cu5TNfaYiQz7jQUbmrhzajXLLxD48
3. Restarted bot processes:
   - pkill -f clawdbot-gateway && pkill -f clawdbot
   - Restarted with nohup clawdbot-gateway
4. Verified API is working with test request

## Status
✅ Bot is now operational with new API key
✅ No quota errors
✅ All services running normally

## Files Modified
- `~/.clawdbot/.env` (NOT committed to git - contains secrets)

## Next Steps
- Monitor API usage at https://ai.dev/rate-limit
- Consider upgrading to paid tier if hitting limits frequently
- Implement rate limiting in bot if needed
