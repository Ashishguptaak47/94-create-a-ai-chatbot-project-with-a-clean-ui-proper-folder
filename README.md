# Modern AI Chatbot

A full-featured, modular AI Chatbot built with **FastAPI**, featuring a responsive modern UI with Server-Sent Events (SSE) streaming, persona switching, conversational memory, and zero-configuration local heuristics plus pluggable LLM support.

## Features

- **Clean, Modern UI**: Dark-themed, responsive design with auto-scroll, message timestamps, persona chips, code formatting, and chat history export.
- **Real-Time Streaming**: Server-Sent Events (SSE) provide low-latency token-by-token streaming.
- **Persona Support**: Switch seamlessly between General Assistant, Code Specialist, Creative Writer, and Tech Strategist.
- **Smart Context Memory**: Windowed conversation memory per session with session resetting.
- **Dual Engine**: Built-in intelligent response generator (math, coding, conversational heuristics, knowledge base) that works out-of-the-box without external API keys, with optional OpenAI/LLM adapter hooks.

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the server**:
   ```bash
   python main.py
   ```

3. **Open the browser**:
   Navigate to `http://localhost:8000`.

## Running Tests

```bash
pytest -v
```

## Project Structure

```text
├── app/
│   ├── api/
│   │   └── routes.py       # REST and SSE API endpoints
│   ├── core/
│   │   ├── bot.py          # Chatbot intelligence engine & personas
│   │   └── memory.py       # Session-based conversational memory
│   ├── static/
│   │   ├── css/style.css   # Clean UI styling
│   │   └── js/app.js       # Dynamic frontend client
│   └── templates/
│       └── index.html      # Glassmorphic chat interface
├── tests/
│   └── test_main.py        # Pytest test suite
├── main.py                 # Application launcher
├── requirements.txt
└── README.md
```
