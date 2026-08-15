Yes. You want **the complete README as one single continuous code block**, with no separate blocks inside it. Copy everything below and paste it directly into `README.md`.

```markdown
# AI Conversational Data Analytics Assistant

An AI-powered conversational assistant built with Python, Streamlit, Google Gemini API, and conversation memory.

The application provides a web-based conversational interface where users can interact with an AI assistant using natural language. The project focuses on building a structured conversational AI pipeline with session-based memory, sliding-window context management, token-aware history pruning, input validation, Gemini-powered response generation, error handling, and automated testing.

## Project Overview

The AI Conversational Data Analytics Assistant is a Streamlit-based AI application designed to demonstrate how a conversational AI system can maintain context across multiple user interactions.

The application follows a modular architecture that separates the user interface, LLM integration, conversation memory, data models, configuration, utilities, skills, and automated testing.

The main conversational workflow is:

1. Accept a user's message.
2. Validate the input.
3. Store the user message in conversation memory.
4. Retrieve the active conversation history.
5. Apply sliding-window context management.
6. Estimate and control conversation token usage.
7. Build a contextual prompt.
8. Send the prompt to Google Gemini.
9. Receive the generated response.
10. Store the assistant response in memory.
11. Display the response through the Streamlit interface.

## Key Features

### Gemini-Powered AI Responses

The application integrates Google's Gemini API through the `google-genai` Python SDK.

The LLM client is responsible for:

- Initializing the Gemini client.
- Sending prompts to Gemini.
- Configuring model parameters.
- Receiving generated responses.
- Handling API-related failures.
- Retrying requests when appropriate.

### Conversation Memory

The project implements a dedicated `ConversationMemoryManager` for maintaining conversation state.

Each conversation has a unique session ID and stores messages according to their roles:

- User
- Assistant
- System

This allows the application to maintain context across multiple conversation turns.

### Sliding-Window Context Management

Conversation history is controlled using a sliding-window mechanism to prevent unlimited conversation history from being sent to the LLM.

The memory manager supports:

- Maximum conversation turns.
- Maximum estimated token limits.
- Preservation of complete user-assistant pairs.
- Preference for the newest conversation pairs.
- Preservation of system messages.
- Removal of older conversation pairs when limits are reached.

This helps control prompt size and prevents unnecessary growth of the conversation context.

### Token Estimation

The project implements lightweight token estimation using a character-based heuristic.

The approximate rule used is:

`1 token ≈ 4 characters`

The estimated token count is used when determining which conversation pairs can remain inside the active context window.

### Context-Aware Conversation

The LLM pipeline builds a contextual prompt using the active conversation history.

For example:

User: My name is John and I am learning Python.

Assistant: Nice to meet you! Python is a great language to learn.

User: What am I learning?

The previous conversation is included when generating the next response, allowing the LLM to understand follow-up questions and maintain conversational context.

### Input Validation

User input is validated before it is sent to the LLM.

Empty messages are rejected so that invalid requests are not unnecessarily sent to the Gemini API.

### API Retry Handling

The Gemini API request layer includes retry handling for temporary request failures.

This provides additional resilience when communicating with the external LLM service.

### Automated Testing

The project includes automated tests covering:

- Conversation memory.
- Sliding-window behavior.
- Memory statistics.
- Input validation.
- Conversation handling.

The current test suite contains 13 tests, all of which passed successfully during validation.

Example result:

`13 passed`

## Project Architecture

The project follows a modular Python architecture:

custom-ai-chatbot/
├── app.py
├── components/
│   ├── __init__.py
│   ├── chat_window.py
│   ├── dataset_summary.py
│   ├── footer.py
│   ├── loading.py
│   ├── metric_cards.py
│   ├── navbar.py
│   └── sidebar.py
├── config/
│   ├── __init__.py
│   └── settings.py
├── core/
│   ├── __init__.py
│   ├── constants.py
│   ├── enums.py
│   ├── exceptions.py
│   └── interfaces.py
├── database/
│   └── __init__.py
├── llm/
│   ├── __init__.py
│   └── client.py
├── memory/
│   ├── __init__.py
│   └── conversation_memory.py
├── models/
│   ├── __init__.py
│   └── chat_models.py
├── pages/
│   ├── chat.py
│   └── home.py
├── skills/
│   ├── __init__.py
│   ├── analytics_skill.py
│   ├── chat_skill.py
│   ├── flashcard_skill.py
│   ├── quiz_skill.py
│   ├── report_skill.py
│   ├── research_skill.py
│   ├── resume_skill.py
│   ├── summary_skill.py
│   └── translation_skill.py
├── tests/
│   ├── test_memory.py
│   ├── test_memory_exam.py
│   └── test_validation.py
├── utils/
│   ├── __init__.py
│   └── logger.py
├── .env
├── .gitignore
├── README.md
└── requirements.txt

The `.env` file is intentionally excluded from GitHub using `.gitignore` so that API credentials are not committed to the repository.

## Application Flow

The overall application flow is:

User
↓
Streamlit Interface
↓
Input Validation
↓
ConversationMemoryManager
↓
Store User Message
↓
Retrieve Conversation History
↓
Sliding-Window Pruning
↓
Contextual Prompt Construction
↓
Gemini LLM Client
↓
Google Gemini API
↓
Generated Response
↓
Store Assistant Response
↓
Display Response in Streamlit

## Conversation Memory Flow

For every user request, the memory pipeline works as follows:

1. The user enters a message.
2. The message is validated.
3. The user message is stored.
4. Conversation history is retrieved.
5. Sliding-window pruning is applied.
6. Relevant conversation history is added to the prompt.
7. The prompt is sent to Gemini.
8. Gemini generates a response.
9. The assistant response is stored.
10. The response is displayed to the user.

## Technologies Used

### Programming Language

- Python 3.11

### Frontend and User Interface

- Streamlit

### Artificial Intelligence and LLM

- Google Gemini API
- google-genai

### Data Processing

- Pandas
- NumPy
- OpenPyXL

### Visualization

- Matplotlib
- Plotly
- Altair

### Configuration and Validation

- Python Dotenv
- Pydantic

### Testing

- Pytest

### Development and Version Control

- Git
- GitHub
- VS Code

## Installation

Follow the steps below to run the project locally.

### 1. Clone the Repository

Clone the GitHub repository:

`git clone https://github.com/guttimahammad369-wq/Task-1-Gutti-Mahammad.git`

Move into the project directory:

`cd Task-1-Gutti-Mahammad`

### 2. Create a Virtual Environment

Create a Python virtual environment:

`python3 -m venv .venv`

### 3. Activate the Virtual Environment

For macOS or Linux:

`source .venv/bin/activate`

For Windows:

`.venv\Scripts\activate`

After activation, the terminal should display something similar to:

`(.venv)`

### 4. Install Dependencies

Install the dependencies listed in `requirements.txt`:

`python -m pip install -r requirements.txt`

### 5. Configure the Gemini API Key

Create a `.env` file in the root directory of the project.

Add:

`GEMINI_API_KEY=your_gemini_api_key_here`

Replace `your_gemini_api_key_here` with your actual Gemini API key.

Never commit your API key to GitHub.

The project `.gitignore` contains `.env`, which prevents the environment file from being tracked by Git.

### 6. Run the Application

Make sure the virtual environment is activated.

Run the Streamlit application:

`python -m streamlit run app.py`

After starting the application, Streamlit will provide a local address similar to:

`http://localhost:8501`

Open the address in your browser to use the application.

## Running Tests

The project's automated tests can be executed with:

`python -m pytest -q tests/test_memory.py tests/test_validation.py tests/test_memory_exam.py`

Expected result:

`13 passed`

You can also execute all available tests using:

`python -m pytest -q`

## Verify Core Dependencies

To verify that the main dependencies are installed correctly, run:

`python -c "import streamlit; import google.genai; import pydantic; import dotenv; print('Core dependencies OK')"`

Expected output:

`Core dependencies OK`

## Testing Conversation Memory Without Gemini API

The conversation memory system can be tested independently without consuming Gemini API quota.

Example:

`from memory.conversation_memory import ConversationMemoryManager

memory = ConversationMemoryManager()

memory.add_user_message(
    "My name is John and I am learning Python."
)

memory.add_assistant_message(
    "Nice to meet you! Python is a great language to learn."
)

history = memory.get_sliding_window_history()

print(history)`

This allows the memory subsystem to be validated independently from the external LLM service.

## Configuration

Application configuration is maintained in:

`config/settings.py`

Keeping configuration in a dedicated module separates configurable values from the main application logic.

Configuration includes values related to:

- Gemini model configuration.
- LLM temperature.
- Maximum output tokens.
- Conversation memory limits.
- Conversation history token limits.
- Environment configuration.

## Gemini API Quota

The application uses the Gemini API, so requests are subject to Google's API quotas and rate limits.

If the application returns:

`429 RESOURCE_EXHAUSTED`

it means the configured Gemini API project has exceeded its available quota or request limit.

This is an external API limitation and does not mean that the conversation-memory implementation or automated tests are broken.

The memory and validation tests can still be executed locally without making Gemini API requests:

`python -m pytest -q tests/test_memory.py tests/test_validation.py tests/test_memory_exam.py`

## Environment Variables

The application uses environment variables for sensitive configuration.

Example:

`GEMINI_API_KEY=your_gemini_api_key_here`

API keys should never be hard-coded inside Python source files.

The `.env` file should never be committed to GitHub.

## Git and GitHub

The project is maintained using Git and GitHub.

Check the current repository status:

`git status`

Add changes:

`git add .`

Create a commit:

`git commit -m "Update project"`

Push changes to GitHub:

`git push`

The project repository is available at:

https://github.com/guttimahammad369-wq/Task-1-Gutti-Mahammad

## Files Excluded From Version Control

The project uses `.gitignore` to prevent unnecessary or sensitive files from being uploaded to GitHub.

Examples include:

- `.venv/`
- `.env`
- `__pycache__/`
- `*.pyc`
- `.pytest_cache/`
- `*.log`
- `.DS_Store`
- `.vscode/`
- `.idea/`
- `archive/`

This keeps the repository clean and prevents sensitive information such as API credentials from being exposed.

## Project Objectives

The main objectives of this project were:

- Build a conversational AI application.
- Integrate Google Gemini with a Python application.
- Develop session-based conversation memory.
- Maintain context across multiple conversation turns.
- Implement sliding-window conversation pruning.
- Control conversation history using token estimation.
- Build a modular application architecture.
- Implement input validation.
- Add automated testing.
- Handle external LLM API requests.
- Implement API retry handling.
- Build a Streamlit-based user interface.
- Manage the project using Git and GitHub.

## Learning Outcomes

This project provided practical experience with:

- Python application development.
- Streamlit application development.
- Large Language Model API integration.
- Google Gemini API.
- Prompt construction.
- Conversational AI.
- Session management.
- Conversation memory.
- Context-window management.
- Sliding-window algorithms.
- Token estimation.
- Input validation.
- Error handling.
- API retry mechanisms.
- Environment variable management.
- Automated testing using Pytest.
- Git version control.
- GitHub repository management.

## Project Validation

The application and supporting components were validated through automated testing and manual execution.

Automated test result:

`13 passed`

Core dependency verification:

`Core dependencies OK`

Git whitespace validation:

`git diff --check`

The conversation-memory pipeline was also manually tested to verify that previous user and assistant messages are included in subsequent prompts.

## Future Improvements

Potential future improvements include:

- Persistent conversation storage.
- Database-backed chat history.
- User authentication.
- Multiple user sessions.
- Model-specific token counting.
- Streaming Gemini responses.
- Improved API quota handling.
- Additional automated tests.
- Cloud deployment.
- Expanded data analytics capabilities.
- More advanced dataset interaction.
- Improved conversation management.

## Author

Gutti Mahammad

GitHub:

https://github.com/guttimahammad369-wq

## Project Status

Completed

The project contains a working Streamlit application, Google Gemini integration, structured conversation memory, sliding-window context management, configuration management, input validation, API retry handling, automated tests, and GitHub version control.
```
