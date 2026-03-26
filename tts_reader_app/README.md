# OpenAI TTS Reader App

A web app that converts typed text or uploaded documents (`.txt`, `.pdf`, `.doc`, `.docx`) into speech using the OpenAI Text-to-Speech API.

## Features

- Paste text directly or upload a supported file.
- Configure:
  - model
  - voice type
  - speed
  - output audio format
  - language selection (including Urdu)
  - style/nature instructions (tone, delivery, mood)
- In-browser playback and one-click download.

## Requirements

- Python 3.10+
- An OpenAI API key
- For `.doc` support: install system parser tools such as `antiword` or `catdoc`.

## Setup

```bash
cd tts_reader_app
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Secure API key setup

### Option A (recommended for local dev): `.env` file

```bash
cp .env.example .env
# edit .env and set OPENAI_API_KEY
```

`main.py` loads `.env` automatically with `python-dotenv`, and `.env` is gitignored.

### Option B: shell environment variable

```bash
export OPENAI_API_KEY="your_api_key_here"
```

### Security tips

- Never hardcode API keys in code.
- Never commit `.env` to Git.
- Rotate keys if you think they were exposed.
- In production, use your host's secret manager (e.g., AWS/GCP/Azure/Vercel/Render secrets) instead of `.env` files in source control.

## Run

```bash
uvicorn main:app --reload --port 8000
```

Open: `http://127.0.0.1:8000`

## Quick usage flow

1. Paste text or upload a file.
2. Choose model, voice, language (Urdu supported), speed, format, and style instructions.
3. Click **Generate speech**.
4. Play audio in-browser or download it.

## Notes

- If both typed text and a file are provided, the uploaded file text is used.
- Large text is capped at 40,000 characters per request to avoid oversized payloads.
- `.doc` parsing depends on system tools and may vary by environment.
- If `OPENAI_API_KEY` is missing, the API returns a clear configuration error.
