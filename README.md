# ABM Lead Generation System

An intelligent lead generation system that uses AI to analyze company websites, generate personalized value propositions, and create tailored outreach messages.

## Architecture

The system is built using:
- **smolagents**: For structured agent-based processing
- **Together.ai**: For LLM operations with various models
- **Gradio**: For the user interface
- **Google Sheets**: For lead management

### Key Components

1. **Agents**:
   - Company Analyzer: Analyzes company websites and identifies export operations
   - Value Proposition Generator: Creates personalized value propositions
   - Message Personalizer: Generates tailored outreach messages

2. **Services**:
   - Together.ai Service: Handles LLM operations
   - Google Sheets Service: Manages lead data
   - Messaging Service: Handles email and SMS communications

3. **Configuration**:
   - LLM settings for different use cases
   - Agent configurations
   - API credentials

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env
# Edit .env with your credentials
```

3. Get Together.ai API key:
   - Sign up at https://www.together.ai/
   - Get your API key from the dashboard
   - Add to .env: `TOGETHER_API_KEY=your_key_here`

4. Set up Google Sheets:
   - Create a new Google Sheet
   - Share with the service account email
   - Add sheet ID to .env

## Usage

1. Start the application:
```bash
python src/app.py
```

2. Access the Gradio interface at http://localhost:7860

3. Use the interface to:
   - View pending leads
   - Run the agent on selected leads
   - Monitor processing logs
   - Send personalized messages

## Development

### Project Structure
```
src/
├── agents/           # Agent implementations
├── config/           # Configuration files
├── services/         # Service implementations
├── ui/              # Gradio interface
└── app.py           # Main application
```

### Testing
```bash
pytest tests/
```

### Available Models
- mistral-7b
- llama-2-70b
- mixtral-8x7b
- codellama-34b

## Features

1. **Intelligent Analysis**:
   - Website content analysis
   - Export operation detection
   - Pain point identification
   - Feature matching

2. **Personalization**:
   - Company-specific value propositions
   - Tailored outreach messages
   - Multi-channel support (email, SMS)

3. **Automation**:
   - Lead processing pipeline
   - Message generation
   - Communication handling

4. **Monitoring**:
   - Processing logs
   - Success rates
   - Error tracking

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License
