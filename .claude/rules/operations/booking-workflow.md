# Booking Workflow

> Standard operating procedure for new bookings
> Last updated: 2026-02-02

## Step 1: Initial Enquiry

**When client contacts (email/SMS/call):**

1. **Greet professionally:** "Hi, thanks for contacting Clean Up Bros!"
2. **Ask key questions:**
   - What type of clean? (End of lease, general, Airbnb)
   - How many bedrooms?
   - Location/suburb?
   - Preferred date and time?
3. **Provide quote** (use pricing.md rules)
4. **Mention bond-back guarantee** (if end of lease)

**Example response:**
```
Hi Sarah!

Thanks for your enquiry. For a 2BR end of lease clean in Liverpool, 
our quote is $380 (inc. GST).

This includes:
- Full bond-back guarantee
- All rooms, kitchen, bathroom
- Oven, windows, carpets

Available dates: [check calendar]

Ready to book? Just confirm and I'll send through the details.

- Bella (Clean Up Bros)
```

## Step 2: Booking Confirmation

**Once client confirms:**

1. **Create calendar event:**
   - Tool: `google_calendar_create_event`
   - Title: "[Client Name] - [Service] - [Address]"
   - Duration: Estimate from pricing table
   - Location: Full address

2. **Create Square invoice:**
   - Tool: `square_create_invoice`
   - Amount: Agreed price
   - Due: 7 days after clean
   - Description: Service details

3. **Send confirmation SMS:**
   - Tool: `send_booking_confirmation`
   - Include: Date, time, price, address

4. **Record in Google Sheets:**
   - Sheet: "Bookings"
   - Columns: Date, Client, Service, Amount, Status

**Example SMS:**
```
Hi Sarah!

Your Clean Up Bros booking is confirmed:

Date: 05/02/2026
Time: 10:00 AM
Service: 2BR End of Lease Clean
Address: 45 Smith St, Liverpool
Price: $380 (inc. GST)

We'll send a reminder 24 hours before.

Questions? Call 0406 764 585

- Clean Up Bros
```

## Step 3: 24-Hour Reminder

**Automated (via heartbeat):**

- Check calendar for bookings tomorrow
- Send reminder SMS via `send_reminder`

**Example reminder:**
```
Hi Sarah!

Just a reminder - your cleaning is tomorrow:

Date: 05/02/2026
Time: 10:00 AM
Address: 45 Smith St, Liverpool

Please ensure access is available. See you tomorrow!

- Clean Up Bros
```

## Step 4: Day of Clean

**Morning of:**
- Confirm cleaner assigned
- Check access arrangements
- Note any special requests

**After clean:**
- Confirm completion
- Note any issues

## Step 5: Post-Clean Follow-Up

**Same day:**

1. **Send completion message:**
   ```
   Hi Sarah! Your clean is complete. 
   
   Payment of $380 is due within 7 days.
   
   Pay online: [Square link]
   Bank: Clean Up Bros, BSB 062-000, Acc 1234567
   
   We hope you love your sparkling space!
   ```

2. **Request review** (if paid on time):
   - Wait 1 day
   - Send review request via `send_review_request_wa`

## Step 6: Payment Tracking

**If not paid within 7 days:**
- Day 8: Friendly reminder
- Day 14: Second reminder
- Day 21: Final notice + $50 late fee

## Checklist Template

```
Booking: [Client Name] - [Date]

[ ] Initial enquiry received
[ ] Quote provided: $[amount]
[ ] Client confirmed booking
[ ] Calendar event created
[ ] Square invoice created: INV-[number]
[ ] Confirmation SMS sent
[ ] Recorded in Google Sheets
[ ] 24h reminder sent (auto)
[ ] Clean completed
[ ] Completion message sent
[ ] Payment received
[ ] Review requested
```
