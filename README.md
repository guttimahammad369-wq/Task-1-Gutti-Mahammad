# AI Conversational Assistant

An AI-powered conversational chatbot built with Python, Streamlit, Gemini, and a stateful conversation-memory system.

The project focuses on maintaining useful conversational context while controlling the amount of history sent to the LLM through sliding-window memory management.

## Features

- Stateful conversation memory
- Unique session-based memory
- User and assistant message tracking
- Input validation
- FIFO conversation pruning
- Maximum conversation-turn limit
- Token-based context pruning
- Complete user-assistant pair preservation
- Sliding-window conversation context
- Conversation clearing
- Gemini LLM integration
- Streamlit chat interface
- Automated tests

## Architecture

```text
User
 |
 v
Streamlit Chat Interface
 |
 v
Input Validation
 |
 v
Conversation Memory Manager
 |
 +----------------------+
 |                      |
 v                      v
Turn Limit          Token Limit
 |                      |
 +----------+-----------+
            |
            v
   Recent Complete
 Conversation Pairs
            |
            v
       Gemini LLM
            |
            v
    Assistant Response
            |
            v
   Conversation Memory