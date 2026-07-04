# Shadow Shield

**Shadow Shield** is a simple project to keep your personal data (PII) safe when sending messages to cloud LLMs.

<video src="https://github.com/user-attachments/assets/2e14460e-6fb2-41c4-a51f-2874b8a3041a" controls width="100%"></video>

## The Problem

When we talk to cloud-based LLMs (like those from OpenAI, Google, Anthropic, etc.), we often send sensitive information—names, email addresses, phone numbers, or banking details. This data can get stored, analyzed, or used for training, posing a privacy risk.

## The Solution

**Shadow Shield** acts as a local proxy (or "shield") between you and the cloud LLM:
1. It intercepts your prompt locally.
2. It uses a small, local model (running via **Ollama**) to find and replace sensitive data with generic placeholders (e.g. `<NAME_1>`, `<EMAIL_1>`).
3. It sends the safe, anonymized prompt to the cloud LLM (in this project via **OpenRouter**).
4. Once the response is received, it swaps the placeholders back with your real data locally.

The entire process is orchestrated as a simple state graph using **LangGraph**.

---

## How to Try It

### 1. Requirements

- **Python 3.11+**
- **Ollama** installed and running locally with the `gemma4:e2b` model:
  ```bash
  ollama run gemma4:e2b
  ```
- An API key for **OpenRouter** (to make cloud LLM calls).

### 2. Installation

Set up a virtual environment and install dependencies:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configuration

Create a `.env` file from the example:
```bash
cp .env.example .env
```
Open `.env` and configure your API keys and model preferences. You can customize the models by changing the `OLLAMA_MODEL` and `OPENROUTER_MODEL` variables to use any local and cloud models of your choice:
```env
OLLAMA_MODEL=gemma4:e2b
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=google/gemini-3.5-flash
```

### 4. Run the Server

Start the FastAPI application:
```bash
python main.py
```

### 5. Send a Test Chat

Use `curl` to send a prompt containing sensitive data:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_session_1",
    "message": "My name is Andrea Emmi, my email is andrea@example.com. Can you refund to IT60D0123456789012345678901? If you have issues call 3331234567."
  }'
```

The server console will print the trace of the anonymization, the cloud call, and the final restored response.
