# RigRav Voice Agent

A real-time AI voice assistant built using LiveKit Agents.
The assistant supports speech-to-text, LLM reasoning, text-to-speech, silence detection, and interruption handling.

---

## Features

- Real-time voice interaction
- Automatic turn detection
- Silence reminder after 20 seconds of inactivity
- Agent interruption when user speaks
- Clean async state management
- Noise cancellation support

---

## SDKs & Technologies Used

- LiveKit Agents SDK
- OpenAI (LLM)
- Deepgram (Speech-to-Text)
- Cartesia (Text-to-Speech)
- Silero VAD (Voice Activity Detection)
- Python 3.10+

---

## External Services

This agent depends on the following third-party services:

- LiveKit (Realtime room & media transport)
- OpenAI API (LLM reasoning)
- Deepgram API (STT)
- Cartesia API (TTS)

You must have valid API keys for these services. find them in LiveKit dashboard

---

## Required Environment Variables

Create a `.env.local` file in the root directory:

```

LIVEKIT_URL=<LIVEKIT_URL>
LIVEKIT_API_KEY=<LIVEKIT_API_KEY>
LIVEKIT_API_SECRET=<LIVEKIT_API_SECRET>

```

Make sure all keys are valid before running.

---

## Setup Instructions

1. Clone the repository

```

git clone https://github.com/Ms-Shahid/RigRag-Voice-Agent
cd RigRag-Voice-Agent

```

2. Create and activate virtual environment

```
python -m venv venv
source venv/bin/activate     # macOS/Linux
venv\Scripts\activate        # Windows

```

3. Install the dependencies

```
pip3 install uv
brew install livekit-cli
uv run src/agent.py download-files
```

4. once the LiveKit dashboard login in done, Authenticate via browser.
```
lk cloud auth
```

5. Add `.env.local` with required keys & check your `.env.local`

```
lk app env -w
```

Start the agent server in dev env:
```
uv run agent.py console
```

The agent will connect to LiveKit and wait for a room session, you can speak & interrupt anytime to change or modify your questions.

---

## 🧠 How Silence Handling Works

- Tracks last speech timestamp
- If user and agent are silent for 20+ seconds
- Agent generates a short reminder
- Cooldown logic prevents repeated audio loops

---

## ⚠️ Known Limitations
- Requires stable internet connection
- Depends on external APIs (network latency affects response time)
- No persistent conversation memory
- No multi-agent orchestration
- Silence detection relies on VAD accuracy

---

## 📌 Architecture Overview

User Speech  
→ STT (Deepgram)  
→ LLM (OpenAI)  
→ TTS (Cartesia)  
→ LiveKit audio output  

With:
- Silero VAD for voice detection
- Multilingual turn detection model
- Async silence monitor task

---

