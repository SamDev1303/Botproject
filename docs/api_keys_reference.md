# API Keys Reference - Clean Up Bros / Bella

> **Owner:** Hafsah Nuzhat
> **Last Updated:** 2026-02-03
> **IMPORTANT:** This file contains NO actual API keys - only references and status

---

## Quick Status Check

Run the health check script to verify all services:
```bash
python3 ~/Desktop/🦀/scripts/api_health_check.py
```

---

## Google Services

| Service | Env Variable | Status | Endpoint |
|---------|-------------|--------|----------|
| OAuth Client ID | `GOOGLE_CLIENT_ID` | Configured | accounts.google.com |
| OAuth Client Secret | `GOOGLE_CLIENT_SECRET` | Configured | accounts.google.com |
| OAuth Tokens | `~/.clawdbot/google-oauth-tokens.json` | Check file | oauth2.googleapis.com |
| Gmail | Uses OAuth | Via tokens | gmail.googleapis.com |
| Calendar | Uses OAuth | Via tokens | calendar.googleapis.com |
| Sheets | Uses OAuth + `GOOGLE_SHEETS_ID` | Configured | sheets.googleapis.com |
| Drive | Uses OAuth | Via tokens | drive.googleapis.com |
| Google Ads | `GOOGLE_ADS_DEVELOPER_TOKEN` | Configured | googleads.googleapis.com |
| Google Ads | `GOOGLE_ADS_LOGIN_CUSTOMER_ID` | Configured | Customer: 1164039680 |
| API Key (Gemini) | `GOOGLE_API_KEY` / `GEMINI_API_KEY` | Configured | generativelanguage.googleapis.com |

### Google OAuth Scopes Enabled

- `gmail.send` - Send emails
- `gmail.readonly` - Read emails
- `gmail.modify` - Mark read/unread
- `spreadsheets` - Full Sheets access
- `drive.readonly` - Read Drive files
- `calendar` - Full Calendar access
- `adwords` - Google Ads API

### Re-authorizing Google OAuth

If tokens expire or need new scopes:
```bash
cd ~/Desktop/🦀 && python3 google-oauth-setup.py
```

---

## Square Payments

| Service | Env Variable | Status | Environment |
|---------|-------------|--------|-------------|
| Access Token | `SQUARE_ACCESS_TOKEN` | Production | connect.squareup.com |
| Application ID | `SQUARE_APPLICATION_ID` | Production | App: sq0idp-*** |
| Environment | `SQUARE_ENVIRONMENT` | production | - |
| Sandbox Token | `SQUARE_SANDBOX_ACCESS_TOKEN` | For testing | connect.squareupsandbox.com |
| Sandbox App ID | `SQUARE_SANDBOX_APP_ID` | For testing | - |

### Square API Capabilities

- Create invoices
- Process payments
- Manage customers
- Track transactions

---

## Twilio (SMS/Voice)

| Service | Env Variable | Status | Notes |
|---------|-------------|--------|-------|
| Account SID | `TWILIO_ACCOUNT_SID` | Configured | Main account |
| Auth Token | `TWILIO_AUTH_TOKEN` | Configured | - |
| API Key SID | `TWILIO_API_KEY_SID` | Configured | For sub-auth |
| AU Phone Number | `TWILIO_FROM_NUMBER_AU` | +61468088118 | Outbound calls/SMS |
| Test Account | `TWILIO_TEST_ACCOUNT_SID` | For testing | - |

### Twilio Capabilities

- Send SMS to Australian numbers
- Make voice calls
- Receive webhooks

---

## Meta / WhatsApp / Facebook / Instagram

| Service | Env Variable | Status | Notes |
|---------|-------------|--------|-------|
| Meta App ID | `META_APP_ID` | Configured | Main app |
| Meta App Secret | `META_APP_SECRET` | Configured | - |
| Meta Business ID | `META_BUSINESS_ID` | Configured | Business account |
| System User Token | `META_SYSTEM_USER_TOKEN` | Configured | Long-lived token |
| WhatsApp Business ID | `WHATSAPP_BUSINESS_ACCOUNT_ID` | Configured | - |
| WhatsApp Phone ID | `WHATSAPP_PHONE_NUMBER_ID` | Configured | For sending |
| Instagram App ID | `INSTAGRAM_APP_ID` | Configured | - |

### Meta Capabilities

- WhatsApp Business messaging
- Facebook page management
- Instagram posting

---

## Other Services

### Search & Scraping

| Service | Env Variable | Status | Use Case |
|---------|-------------|--------|----------|
| Brave Search | `BRAVE_API_KEY` | Configured | Web search |
| Apify | `APIFY_API_KEY` | Configured | Web scraping |
| Apify (Additional) | `APIFY_N8N_KEY`, `APIFY_CUB_KEY` | Configured | Multiple accounts |

### AI & Voice

| Service | Env Variable | Status | Use Case |
|---------|-------------|--------|----------|
| ElevenLabs | `ELEVENLABS_API_KEY` | Configured | Voice generation |
| OpenRouter | `OPENROUTER_API_KEY` | Configured | LLM routing |
| OpenAI | `OPENAI_API_KEY` | Configured | Embeddings (needs credits) |

### Communication

| Service | Env Variable | Status | Use Case |
|---------|-------------|--------|----------|
| Telegram Bot | `TELEGRAM_BOT_TOKEN` | Configured | @CubsBookKeeperBot |
| LinkedIn | `LINKEDIN_CLIENT_ID` | Configured | B2B marketing |

### Infrastructure

| Service | Env Variable | Status | Use Case |
|---------|-------------|--------|----------|
| AWS | `AWS_ACCESS_KEY_ID` | Configured | Cloud hosting |
| n8n | `N8N_API_KEY` | Configured | Workflow automation |
| Convex | `CONVEX_DEPLOY_KEY` | Configured | Real-time database |
| Sentry | `SENTRY_ORG_TOKEN` | Configured | Error tracking |

### Video & Media

| Service | Env Variable | Status | Use Case |
|---------|-------------|--------|----------|
| Kie AI | `KIE_AI_API_KEY` | Configured | Video generation |
| REF Tools | `REF_API_KEY` | Configured | Reference tools |

---

## Environment File Location

**All credentials stored in:** `~/.clawdbot/.env`

**File permissions:** `chmod 600 ~/.clawdbot/.env`

**Token file:** `~/.clawdbot/google-oauth-tokens.json`

---

## Security Reminders

1. **NEVER** commit `.env` files to Git
2. **NEVER** share API keys in chat or logs
3. **ALWAYS** use environment variables in code
4. **ROTATE** keys if compromised
5. **CHECK** `.gitignore` includes sensitive files

---

## Troubleshooting

### Service Not Working?

1. Run health check: `python3 ~/Desktop/🦀/scripts/api_health_check.py`
2. Check environment variable is set: `grep SERVICE_NAME ~/.clawdbot/.env`
3. Verify file permissions: `ls -la ~/.clawdbot/.env`
4. For Google: Re-run OAuth setup if tokens expired

### Common Issues

| Issue | Solution |
|-------|----------|
| Google 401 | Re-run `google-oauth-setup.py` |
| Square 401 | Check `SQUARE_ENVIRONMENT` matches token |
| Twilio 401 | Verify Account SID + Auth Token pair |
| WhatsApp 400 | Check Phone Number ID is correct |

---

## Adding New Services

1. Get API credentials from provider
2. Add to `~/.clawdbot/.env`:
   ```bash
   echo "NEW_SERVICE_KEY=your_key_here" >> ~/.clawdbot/.env
   ```
3. Update this reference document
4. Add health check test in `scripts/api_health_check.py`

---

*This file is safe to share - contains no actual credentials*
