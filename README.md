# agentic-demo
agent-demo-track
Gradio Agents &amp; MCP Hackathon 2025

# ABM Lead Generation Agent

An intelligent agent for automated Account-Based Marketing (ABM) lead generation and outreach. This system uses AI to process leads from a Google Sheet, verify contact information, and send personalized outreach messages via email and SMS.

## Features

- 🔄 Automated lead processing from Google Sheets
- ✉️ Multi-channel outreach (Email & SMS)
- ✅ Email verification and validation
- 🤖 AI-powered message personalization
- 📊 Real-time status tracking
- 🎯 Account-based marketing focus
- 📱 Modern web interface

## Prerequisites

- Python 3.8+
- Google Cloud Platform account with Sheets API enabled
- Textfully API key for SMS
- (Optional) Email verification API key

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd abm-lead-gen
```

2. Create and activate a conda environment:
```bash
conda create -n MLHW python=3.8
conda activate MLHW
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables in `.env`:
```
GOOGLE_APPLICATION_CREDENTIALS="/path/to/service_account.json"
SPREADSHEET_ID="your-spreadsheet-id"
WORKSHEET_NAME="Leads"
TEXTFULLY_API_KEY="your-textfully-key"
VERIFY_API_KEY="your-verify-key"  # optional
FROM_EMAIL="your-email@domain.com"
```

## Usage

1. Start the application:
```bash
python app.py
```

2. Open your browser to `http://localhost:7860`

3. Use the interface to:
   - View pending leads
   - Process leads automatically
   - Monitor outreach status
   - View processing logs

## Google Sheets Setup

1. Create a new Google Sheet
2. Share it with the service account email
3. Create a worksheet named "Leads" with these columns:
   - CONTACT_PERSON
   - CONTACT_EMAIL
   - CONTACT_PHONE
   - COMPANY
   - STATUS
   - NOTES
   - TIMESTAMP
   - LAST_UPDATED
   - SOURCE
   - PRIORITY

## Architecture

- `app.py`: Gradio web interface
- `abm_agent.py`: Main agent logic
- `config.py`: Configuration management
- `sheets_service.py`: Google Sheets integration
- `messaging_service.py`: Email and SMS handling

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details
