# ClawdBot - AI Business Assistant Framework

> An open-source AI assistant framework for small business automation. Built with MCP (Model Context Protocol) servers for seamless tool integration.

## Overview

ClawdBot is a modular AI assistant designed to help small businesses automate:
- **Customer Communication** (Email, SMS, WhatsApp, Voice)
- **Bookkeeping & Accounting** (Australian tax compliant)
- **Invoice & Payment Management**
- **Social Media Marketing** (Instagram, Facebook, LinkedIn)
- **Lead Generation & Cold Outreach**
- **Calendar & Scheduling**

---

## Features

### Communication
| Feature | Description |
|---------|-------------|
| Email | Send, read, search emails via Gmail API |
| SMS | Send text messages, booking confirmations, reminders |
| WhatsApp | Business messaging with templates |
| Voice Calls | AI-powered calls with text-to-speech |
| Voice Generation | Professional voice messages via ElevenLabs |

### Business Operations
| Feature | Description |
|---------|-------------|
| Invoicing | Create and send invoices via Square |
| Payment Links | Generate shareable payment links |
| Payment Tracking | Monitor paid/unpaid invoices |
| Expense Recording | Log expenses with GST calculation |
| P&L Reports | Generate profit & loss statements |
| BAS Preparation | Calculate GST for quarterly BAS |

### Marketing
| Feature | Description |
|---------|-------------|
| Instagram Posts | Share photos, carousels, stories |
| Facebook Posts | Business page management |
| LinkedIn Posts | Professional networking content |
| Lead Generation | Find leads via Google Maps/Web |
| Cold Outreach | Email + SMS + Call campaigns |

### Scheduling
| Feature | Description |
|---------|-------------|
| Calendar | View/create events, check availability |
| Booking Confirmations | Automated customer notifications |
| Reminders | 24-hour pre-appointment alerts |

---

## MCP Servers

Each capability is a separate MCP server that can be used independently:

```
mcp/
├── google_server.py      # Gmail, Sheets, Drive, Calendar
├── square_server.py      # Payments & Invoicing
├── accounting_server.py  # Bookkeeping (AU Tax Compliant)
├── twilio_server.py      # SMS & Voice Calls
├── whatsapp_server.py    # WhatsApp Business API
├── elevenlabs_server.py  # Voice Generation
├── meta_server.py        # Instagram & Facebook
├── linkedin_server.py    # LinkedIn Posting
├── brave_server.py       # Web Search
├── apify_server.py       # Web Scraping
├── coldoutreach_server.py # Lead Campaigns
└── kie_server.py         # AI Video Generation
```

---

## Installation

### Prerequisites
- Python 3.10+
- MCP-compatible AI client (Claude Desktop, etc.)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/SamDev1303/Botproject.git
cd Botproject
```

2. Create virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install mcp fastmcp
```

4. Create environment file:
```bash
cp .env.example .env
# Edit .env with your API keys
```

5. Configure MCP servers in your AI client.

---

## Configuration

### Environment Variables

Create a `.env` file with your API credentials:

```env
# Google (OAuth2)
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REFRESH_TOKEN=your_refresh_token
GOOGLE_SHEETS_ID=your_spreadsheet_id

# Square Payments
SQUARE_ACCESS_TOKEN=your_access_token
SQUARE_APPLICATION_ID=your_app_id
SQUARE_ENVIRONMENT=production  # or sandbox

# Twilio (SMS/Calls)
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# WhatsApp Business
META_SYSTEM_USER_TOKEN=your_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_id
WHATSAPP_BUSINESS_ACCOUNT_ID=your_account_id

# ElevenLabs (Voice)
ELEVENLABS_API_KEY=your_api_key

# Meta (Facebook/Instagram)
META_APP_ID=your_app_id
META_APP_SECRET=your_app_secret

# LinkedIn
LINKEDIN_CLIENT_ID=your_client_id
LINKEDIN_CLIENT_SECRET=your_client_secret
LINKEDIN_ACCESS_TOKEN=your_access_token

# Brave Search
BRAVE_API_KEY=your_api_key

# Apify (Web Scraping)
APIFY_API_KEY=your_api_key

# Gmail SMTP
GMAIL_ADDRESS=your_email@gmail.com
GMAIL_APP_PASSWORD=your_app_password
```

### MCP Client Configuration

Add to your MCP client config (e.g., Claude Desktop):

```json
{
  "mcpServers": {
    "google": {
      "command": "python3",
      "args": ["path/to/mcp/google_server.py"]
    },
    "square": {
      "command": "python3",
      "args": ["path/to/mcp/square_server.py"]
    },
    "accounting": {
      "command": "python3",
      "args": ["path/to/mcp/accounting_server.py"]
    }
  }
}
```

---

## Usage Examples

### Bookkeeping

```
"Record income: $380 from Sarah Chen for end of lease cleaning"
"Add expense: $45.50 at Bunnings for cleaning supplies"
"Show me profit and loss for this month"
"Prepare my BAS for this quarter"
```

### Customer Communication

```
"Send booking confirmation to 0412345678 for tomorrow at 9am"
"Send payment reminder to clients with overdue invoices"
"Create a payment link for $480"
```

### Marketing

```
"Post to Instagram: [image] with caption about our latest transformation"
"Find property managers in Liverpool NSW"
"Start cold email campaign to new leads"
```

---

## Australian Tax Compliance

The accounting module is built for Australian small businesses:

- **GST Calculation**: Automatic GST = Total ÷ 11
- **BAS Preparation**: Quarterly GST reporting
- **Expense Categories**: ATO-compliant categories
- **Superannuation**: 11.5% super calculation
- **Financial Year**: July-June reporting
- **Tax Deductions**: Built-in deductibility checks

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    AI ASSISTANT                         │
│              (Claude, GPT, Gemini, etc.)                │
└─────────────────────────┬───────────────────────────────┘
                          │ MCP Protocol
┌─────────────────────────┴───────────────────────────────┐
│                    MCP SERVERS                          │
├──────────┬──────────┬──────────┬──────────┬────────────┤
│  Google  │  Square  │ Twilio   │  Meta    │ Accounting │
│  Gmail   │ Payments │  SMS     │ Instagram│ Bookkeeping│
│  Sheets  │ Invoices │  Voice   │ Facebook │ GST/BAS    │
│ Calendar │          │          │ LinkedIn │            │
└──────────┴──────────┴──────────┴──────────┴────────────┘
                          │
┌─────────────────────────┴───────────────────────────────┐
│                  EXTERNAL APIs                          │
│    Google • Square • Twilio • Meta • ElevenLabs • etc   │
└─────────────────────────────────────────────────────────┘
```

---

## Dashboard

Optional web dashboard for monitoring:

```
bella-dashboard/
├── index.html       # Dashboard UI
├── fetch-messages.py # Sync with Telegram
├── status.json      # Current status
└── messages.json    # Recent messages
```

Features:
- Real-time status display
- Message inbox
- Activity feed
- Health monitoring

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## Security

**Important:** Never commit your `.env` file or any files containing API keys.

The `.gitignore` is configured to exclude:
- Environment files (`.env`, `*.env`)
- OAuth tokens (`*-oauth-tokens.json`)
- Credentials files (`credentials.json`)
- Personal data files

---

## License

MIT License - See [LICENSE](LICENSE) for details.

---

## Support

- Issues: [GitHub Issues](https://github.com/SamDev1303/Botproject/issues)
- Documentation: [Wiki](https://github.com/SamDev1303/Botproject/wiki)

---

## Credits

Built with:
- [MCP (Model Context Protocol)](https://modelcontextprotocol.io)
- [FastMCP](https://github.com/jlowin/fastmcp)
- [Google APIs](https://developers.google.com)
- [Square API](https://developer.squareup.com)
- [Twilio](https://www.twilio.com)
- [ElevenLabs](https://elevenlabs.io)
- [Meta Business API](https://developers.facebook.com)
