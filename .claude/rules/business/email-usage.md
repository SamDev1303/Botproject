# Email Usage Guide

> **CRITICAL:** Always use the correct email addresses
> **Last Updated:** 2026-02-02

---

## ✅ CORRECT Email Addresses

### Business Email (Clean Up Bros)
**Use for ALL business communication:**

```
cleanupbros.au@gmail.com
```

**When to use:**
- Customer inquiries
- Invoices
- Booking confirmations
- Marketing emails
- Cold outreach
- Any Clean Up Bros business

**Environment variable:**
```bash
BUSINESS_EMAIL=cleanupbros.au@gmail.com
HAFSAH_BUSINESS_EMAIL=cleanupbros.au@gmail.com
```

---

### Personal Email (Hafsah)
**Use only for personal matters:**

```
hafsahnuzhat1303@gmail.com
```

**When to use:**
- Personal reminders
- Non-business notifications
- Private communications

**Environment variable:**
```bash
HAFSAH_PERSONAL_EMAIL=hafsahnuzhat1303@gmail.com
GMAIL_ADDRESS=hafsahnuzhat1303@gmail.com
```

---

## ❌ WRONG Email Addresses - NEVER USE

### DO NOT USE:
```
❌ hafsah@cleanupbros.com.au  (WRONG - does not exist)
❌ hafsah@neno.com.au         (WRONG - does not exist)
❌ Any other variation
```

**These addresses DO NOT WORK and will cause errors.**

---

## 📋 Email Usage Rules

### Default Behavior
**When sending emails for Clean Up Bros:**

1. **From:** `cleanupbros.au@gmail.com`
2. **Reply-To:** `cleanupbros.au@gmail.com`
3. **Signature:** Clean Up Bros details

### Code Implementation
```python
# Always use environment variable
from_email = os.environ.get('BUSINESS_EMAIL', 'cleanupbros.au@gmail.com')

# NEVER hardcode email addresses
# ❌ BAD: from_email = "hafsah@cleanupbros.com.au"
# ✅ GOOD: from_email = os.environ.get('BUSINESS_EMAIL')
```

---

## 🔍 Where Emails Are Configured

### 1. Environment Variables
**File:** `~/.clawdbot/.env`
```bash
BUSINESS_EMAIL=cleanupbros.au@gmail.com
HAFSAH_PERSONAL_EMAIL=hafsahnuzhat1303@gmail.com
GMAIL_ADDRESS=hafsahnuzhat1303@gmail.com
```

### 2. Google MCP Server
**File:** `mcp/google_server.py`
- Uses `GMAIL_ADDRESS` from environment
- Sends from authenticated Gmail account

### 3. Cold Outreach Server
**File:** `mcp/coldoutreach_server.py`
- Should use `BUSINESS_EMAIL` for campaigns

---

## ✉️ Email Templates

### Business Communication
```
From: Clean Up Bros <cleanupbros.au@gmail.com>
To: [Customer]
Subject: [Topic]

Hi [Name],

[Message]

Best regards,
Hafsah
Clean Up Bros
0406 764 585
cleanupbros.com.au
```

### Personal Communication
```
From: Hafsah <hafsahnuzhat1303@gmail.com>
To: [Recipient]
Subject: [Topic]

[Message]

- Hafsah
```

---

## 🚨 Troubleshooting

### If Bella uses wrong email:

1. **Check environment variables:**
   ```bash
   grep EMAIL ~/.clawdbot/.env
   ```

2. **Restart Clawdbot:**
   ```bash
   pkill -f clawdbot && clawdbot
   ```

3. **Check this file is loaded:**
   - Auto-loaded from `.claude/rules/business/email-usage.md`
   - Should appear in context on every session

---

## 📝 Summary

**Business Email:**
- ✅ `cleanupbros.au@gmail.com` (CORRECT)

**Personal Email:**
- ✅ `hafsahnuzhat1303@gmail.com` (CORRECT)

**NEVER USE:**
- ❌ `hafsah@cleanupbros.com.au` (DOES NOT EXIST)
- ❌ `hafsah@neno.com.au` (DOES NOT EXIST)

---

**When in doubt:** Use `cleanupbros.au@gmail.com` for ALL business communication.
