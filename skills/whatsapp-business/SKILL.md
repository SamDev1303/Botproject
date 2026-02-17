---
name: whatsapp-business
description: WhatsApp Business API — send messages, booking confirmations, payment reminders, review requests, and media messages. Use when the user asks to WhatsApp a client, send a WhatsApp message, or communicate via WhatsApp.
---

# WhatsApp Business

Send business messages via the WhatsApp Business Cloud API (Meta Graph API v18.0).

## Prerequisites

- **Env vars**: `META_SYSTEM_USER_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`
- **API base**: `https://graph.facebook.com/v18.0`
- **Business account**: `WHATSAPP_BUSINESS_ACCOUNT_ID`

## API Helper

```python
import os, json, urllib.request

TOKEN = os.environ['META_SYSTEM_USER_TOKEN']
PHONE_ID = os.environ['WHATSAPP_PHONE_NUMBER_ID']
BASE = "https://graph.facebook.com/v18.0"

def wa(endpoint, data=None, method='GET'):
    url = f"{BASE}{endpoint}"
    req = urllib.request.Request(url,
        headers={'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'},
        method=method)
    if data:
        req.data = json.dumps(data).encode()
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())
```

## Workflows

### 1. Send Text Message

```python
result = wa(f'/{PHONE_ID}/messages', {
    'messaging_product': 'whatsapp',
    'to': '61400000000',  # No + prefix for WhatsApp API
    'type': 'text',
    'text': {'body': 'Hello from Clean Up Bros! 🧹'}
}, 'POST')
print(f"Message ID: {result['messages'][0]['id']}")
```

### 2. Booking Confirmation

```python
def wa_booking_confirmation(to, client_name, date, time, address):
    body = (
        f"Hi {client_name}! ✅\n\n"
        f"Your cleaning is confirmed:\n"
        f"📅 *{date}* at *{time}*\n"
        f"📍 {address}\n\n"
        f"Our team will arrive on time. Please ensure access is available.\n\n"
        f"Reply here if you need to reschedule.\n"
        f"— *Clean Up Bros* 🧹"
    )
    return wa(f'/{PHONE_ID}/messages', {
        'messaging_product': 'whatsapp',
        'to': to,
        'type': 'text',
        'text': {'body': body}
    }, 'POST')
```

### 3. Payment Reminder

```python
def wa_payment_reminder(to, client_name, amount, invoice_num, payment_link=None):
    body = (
        f"Hi {client_name},\n\n"
        f"Friendly reminder: Invoice *#{invoice_num}* for *${amount:.2f}* is outstanding.\n\n"
        f"💳 *Pay online:*\n{payment_link}\n\n" if payment_link else ""
        f"🏦 *Bank transfer:*\n"
        f"Clean Up Bros\n"
        f"BSB: 062-000\n"
        f"Acc: 1234567\n"
        f"Ref: {invoice_num}\n\n"
        f"Thanks! — Clean Up Bros"
    )
    return wa(f'/{PHONE_ID}/messages', {
        'messaging_product': 'whatsapp',
        'to': to,
        'type': 'text',
        'text': {'body': body}
    }, 'POST')
```

### 4. Review Request (Post-Service)

```python
def wa_review_request(to, client_name):
    body = (
        f"Hi {client_name}! 👋\n\n"
        f"Thanks for choosing Clean Up Bros! We hope you're happy with the clean.\n\n"
        f"Would you mind leaving us a quick Google review? It really helps! ⭐\n"
        f"https://g.page/r/cleanupbros/review\n\n"
        f"Thank you! 🙏"
    )
    return wa(f'/{PHONE_ID}/messages', {
        'messaging_product': 'whatsapp',
        'to': to,
        'type': 'text',
        'text': {'body': body}
    }, 'POST')
```

### 5. Send Image / Document

```python
# Send image (by URL)
wa(f'/{PHONE_ID}/messages', {
    'messaging_product': 'whatsapp',
    'to': '61400000000',
    'type': 'image',
    'image': {
        'link': 'https://example.com/before-after.jpg',
        'caption': 'Before & after — Clean Up Bros ✨'
    }
}, 'POST')

# Send document (e.g., invoice PDF)
wa(f'/{PHONE_ID}/messages', {
    'messaging_product': 'whatsapp',
    'to': '61400000000',
    'type': 'document',
    'document': {
        'link': 'https://example.com/invoice.pdf',
        'caption': 'Invoice #1234',
        'filename': 'CleanUpBros_Invoice_1234.pdf'
    }
}, 'POST')
```

### 6. Send Template Message (For first contact / 24h window expired)

```python
# Template messages are pre-approved by Meta
wa(f'/{PHONE_ID}/messages', {
    'messaging_product': 'whatsapp',
    'to': '61400000000',
    'type': 'template',
    'template': {
        'name': 'booking_confirmation',  # Must be approved in Meta Business
        'language': {'code': 'en'},
        'components': [
            {'type': 'body', 'parameters': [
                {'type': 'text', 'text': 'John'},
                {'type': 'text', 'text': 'Tomorrow at 9am'}
            ]}
        ]
    }
}, 'POST')
```

## Phone Number Format

WhatsApp API uses numbers **without** the `+` prefix:
- `+61 400 000 000` → `61400000000`
- `0400 000 000` → `61400000000` (add country code, drop leading 0)

## Important Notes

- **24-hour window**: Free-form messages only within 24h of customer's last message. Outside this window, use approved template messages.
- **WhatsApp formatting**: `*bold*`, `_italic_`, `~strikethrough~`, `` `code` ``
- **Rate limits**: 1,000 messages/day on standard tier
- **Status**: Check `⚠️` in API health — verify `WHATSAPP_PHONE_NUMBER_ID` is correct
- **Never spam**: Only message existing clients or leads who've opted in

## References

- WhatsApp Cloud API: https://developers.facebook.com/docs/whatsapp/cloud-api
- Message types: https://developers.facebook.com/docs/whatsapp/cloud-api/messages
- Template messages: https://developers.facebook.com/docs/whatsapp/cloud-api/guides/send-message-templates
