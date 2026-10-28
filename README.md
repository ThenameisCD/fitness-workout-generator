# Workout Plan Generator

A Streamlit app that generates a weekly workout plan from structured fitness inputs using Groq.

## Features

- Collects fitness goal, experience level, available training days, equipment, and optional limitations.
- Builds a prompt from those inputs and requests a plan from Groq.
- Displays the plan and shows friendly messages for common request failures.

## Setup

1. Install Python 3.11 or newer and [uv](https://docs.astral.sh/uv/).
2. Open a terminal in this project folder and install dependencies:

   ```powershell
   uv sync
   ```

3. Copy `.env.example` to `.env`. In PowerShell, run:

   ```powershell
   Copy-Item .env.example .env
   ```

4. Open `.env` and replace the `GROQ_API_KEY` placeholder with your own Groq API key. Keep the key private; do not commit `.env`.

## Run the app

From the project folder, run:

```powershell
uv run streamlit run app.py
```

Open the local URL printed in the terminal, usually <http://localhost:8501>.

## Safety note

The generated plan is general information, not medical advice. Review the output carefully. For injuries or health limitations, consult a qualified health professional before following a plan.

Never upload `.env` or share your API key. `.env.example` contains placeholders and is safe to include in the repository.