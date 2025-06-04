# LLM Application Flowchart

## Layer 1: User Interface (UI)
- **Gradio Interface** (`src/ui/gradio_interface.py`)
  - Displays pending leads and processing logs.
  - Provides buttons to refresh leads and run the agent.

## Layer 2: Core Agent Logic
- **ABM Lead Generation Agent** (`src/core/abm_agent.py`)
  - Initializes configuration and services.
  - Processes leads by verifying emails and sending messages.
  - Uses smolagents for LLM interactions.

## Layer 3: Services
- **Google Sheets Service** (`src/services/sheets_service.py`)
  - Manages interactions with Google Sheets.
  - Retrieves pending leads and updates lead statuses.
- **Messaging Service** (`src/services/messaging_service.py`)
  - Handles email and SMS communications.
  - Formats and sends messages to leads.

## Layer 4: Configuration
- **Config** (`src/core/config.py`)
  - Loads and validates environment variables.
  - Provides configuration settings for the application.

## Layer 5: Testing
- **Test Suite** (`tests/`)
  - Unit tests for UI, agent logic, and services.
  - Ensures functionality and error handling.

## Layer 6: Application Entry Point
- **Main Application** (`app.py`)
  - Sets up the environment and initializes the Gradio UI.
  - Launches the application on a specified server and port.

```mermaid
graph TD
    subgraph "User Interface"
        UI[Gradio Interface]
        UI --> |Select Leads| LeadSelection[Lead Selection]
        UI --> |View Results| Results[Results Display]
    end

    subgraph "Lead Processing"
        LeadSelection --> |Process| LeadProcessor[Lead Processor]
        LeadProcessor --> |Fetch Data| Sheets[Google Sheets]
        LeadProcessor --> |Analyze| CompanyAnalyzer[Company Analyzer Agent]
        LeadProcessor --> |Generate| ValueProp[Value Proposition Generator Agent]
        LeadProcessor --> |Create| MessagePersonalizer[Message Personalizer Agent]
    end

    subgraph "LLM Operations"
        CompanyAnalyzer --> |Use| TogetherAI[Together.ai Service]
        ValueProp --> |Use| TogetherAI
        MessagePersonalizer --> |Use| TogetherAI
        TogetherAI --> |Models| Models[Available Models]
        Models --> |mistral-7b| Mistral[Mistral 7B]
        Models --> |llama-2-70b| Llama[Llama 2 70B]
        Models --> |mixtral-8x7b| Mixtral[Mixtral 8x7B]
        Models --> |codellama-34b| CodeLlama[CodeLlama 34B]
    end

    subgraph "Communication"
        MessagePersonalizer --> |Send| Email[Email Service]
        MessagePersonalizer --> |Send| SMS[SMS Service]
        Email --> |Status| Results
        SMS --> |Status| Results
    end

    subgraph "Data Flow"
        Sheets --> |Lead Data| LeadProcessor
        CompanyAnalyzer --> |Analysis| ValueProp
        ValueProp --> |Proposition| MessagePersonalizer
        MessagePersonalizer --> |Messages| Results
    end

    subgraph "Configuration"
        Config[LLM Config]
        AgentConfig[Agent Config]
        Config --> TogetherAI
        AgentConfig --> CompanyAnalyzer
        AgentConfig --> ValueProp
        AgentConfig --> MessagePersonalizer
    end

    style UI fill:#f9f,stroke:#333,stroke-width:2px
    style TogetherAI fill:#bbf,stroke:#333,stroke-width:2px
    style CompanyAnalyzer fill:#bfb,stroke:#333,stroke-width:2px
    style ValueProp fill:#bfb,stroke:#333,stroke-width:2px
    style MessagePersonalizer fill:#bfb,stroke:#333,stroke-width:2px
    style Models fill:#fbb,stroke:#333,stroke-width:2px
``` 