---
name: twilio-comms
description: Twilio SMS and voice communications — send SMS, booking confirmations, payment reminders, make outbound calls. Use when the user asks to text a client, send a reminder, confirm a booking via SMS, or make a phone call.
---

# Twilio Comms

SMS and voice communications for Clean Up Bros via Twilio (AU number).

## Prerequisites

- **Env vars**: `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM_NUMBER_AU`
- **AU number**: Configured for Australian SMS and voice
- **API base**: `https://api.twilio.com/2010-04-01/Accounts/{SID}`

## API Helper

```python
import os, json, base64, urllib.request, urllib.parse

SID = os.environ['TWILIO_ACCOUNT_SID']
TOKEN = os.environ['TWILIO_AUTH_TOKEN']
FROM = os.environ['TWILIO_FROM_NUMBER_AU']
BASE = f"https://api.twilio.com/2010-04-01/Accounts/{SID}"
AUTH = base64.b64encode(f"{SID}:{TOKEN}".encode()).decode()

def twilio(method, endpoint, data=None):
    req = urllib.request.Request(f"{BASE}{endpoint}",
        headers={'Authorization': f'Basic {AUTH}'},
        method=method)
    if data:
        req.data = urllib.parse.urlencode(data).encode()
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())
```

## Workflows

### 1. Send SMS

```python
msg = twilio('POST', '/Messages.json', {
    'From': FROM,
    'To': '+61400000000',  # Recipient (E.164 format)
    'Body': 'Hi! Your cleaning is confirmed for tomorrow at 9am. — Clean Up Bros'
})
print(f"Sent: {msg['sid']} — Status: {msg['status']}")
```

### 2. Booking Confirmation Template

```python
def send_booking_confirmation(to, client_name, date, time, address):
    body = (
        f"Hi {client_name}! ✅\n\n"
        f"Your cleaning is confirmed:\n"
        f"📅 {date} at {time}\n"
        f"📍 {address}\n\n"
        f"Reply to this message if you need to reschedule.\n"
        f"— Clean Up Bros 🧹"
    )
    return twilio('POST', '/Messages.json', {'From': FROM, 'To': to, 'Body': body})
```

### 3. Payment Reminder Template

```python
def send_payment_reminder(to, client_name, amount, invoice_num, payment_link=None):
    body = (
        f"Hi {client_name},\n\n"
        f"Friendly reminder: Invoice #{invoice_num} for ${amount:.2f} is outstanding.\n"
    )
    if payment_link:
        body += f"\nPay online: {payment_link}\n"
    body += (
        f"\nBank transfer:\n"
        f"Clean Up Bros\n"
        f"BSB: 062-000\n"
        f"Acc: 1234567\n"
        f"Ref: {invoice_num}\n\n"
        f"Thanks! — Clean Up Bros"
    )
    return twilio('POST', '/Messages.json', {'From': FROM, 'To': to, 'Body': body})
```

### 4. Make Outbound Call

```python
call = twilio('POST', '/Calls.json', {
    'From': FROM,
    'To': '+61400000000',
    'Url': 'http://demo.twilio.com/docs/voice.xml',  # TwiML URL
    'Tts': 'Hello, this is a reminder from Clean Up Bros about your upcoming appointment.'
})
print(f"Call SID: {call['sid']}")
```

For custom call content, use TwiML:
```xml
<Response>
  <Say voice="alice">Hello, this is Clean Up Bros calling about your booking.</Say>
  <Pause length="1"/>
  <Say voice="alice">Press 1 to confirm or 2 to reschedule.</Say>
  <Gather numDigits="1" action="/handle-key"/>
</Response>
```

### 5. Check Message History

```python
messages = twilio('GET', '/Messages.json?PageSize=20')
for m in messages['messages']:
    direction = '→' if m['direction'].startswith('outbound') else '←'
    print(f"{direction} {m['to']} — {m['body'][:50]}... — {m['status']}")
```

## Phone Number Format

Always use E.164 format for Australian numbers:
- `0400 000 000` → `+61400000000`
- `02 9999 9999` → `+6129999999`

## Important Notes

- SMS to AU numbers: ~$0.06 per message
- Voice calls: ~$0.04/min
- Messages over 160 chars are split (billed per segment)
- Always include business name in SMS for trust
- **Never send SMS between 9PM–8AM AEST** unless urgent
- Test with `TWILIO_TEST_ACCOUNT_SID` / `TWILIO_TEST_AUTH_TOKEN` to avoid charges

## References

- Twilio SMS API: https://www.twilio.com/docs/sms/api/message-resource
- Twilio Voice API: https://www.twilio.com/docs/voice/api/call-resource
- TwiML reference: https://www.twilio.com/docs/voice/twiml
