# Workout Plan Generator

A Streamlit app that generates a weekly workout plan from structured fitness inputs using Groq.

## Features

- Collects fitness goal, experience level, available training days, equipment, and optional limitations (checkbox + free text).
- Builds a prompt from those inputs and requests a plan from Groq.
- Displays the plan, preserves it across reruns, and lets users download it as Markdown or Text.
- Regenerates a plan variation with one click.
- Swaps a single exercise in the current plan on demand.
- Shows friendly messages for common request failures and incomplete responses.
- "Regenerate plan" button for a new variation, and "Swap an exercise" to replace one exercise throughout the plan.
- Download the plan as Markdown or plain text.
- A checkbox enables the injury/limitation box; if inputs change after a plan is generated, the old plan is hidden and the user is asked to click Generate Plan again.
- The Generate Plan button is disabled while a current plan is showing; use Regenerate for a new variation, or change an input to enable Generate again.

## Project structure

```
app.py                  # Streamlit UI, prompt building, Groq call, validation
pyproject.toml          # Project metadata and dependencies (uv)
uv.lock                 # Locked dependency versions
requirements.txt        # Same dependencies for pip users
.env.example            # Template for your API key
.streamlit/config.toml  # Streamlit settings
```

## Setup

1. Install Python 3.11 or newer and [uv](https://docs.astral.sh/uv/).
2. Open a terminal in this project folder and install dependencies:

   ```powershell
   uv sync
   ```

   Option B (pip):
   ```powershell
   python -m pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env`. In PowerShell, run:

   ```powershell
   Copy-Item .env.example .env
   ```

   On macOS/Linux:
   ```bash
   cp .env.example .env
   ```

4. Open `.env` and replace the `GROQ_API_KEY` placeholder with your own Groq API key. Keep the key private; do not commit `.env`.

## Run the app

From the project folder, run:

```powershell
uv run streamlit run app.py
```

pip alternative:

```powershell
python -m streamlit run app.py
```

Open the local URL printed in the terminal, usually <http://localhost:8501>.

## Prompt design

- System prompt (fixed rules): output format (Markdown, exactly 7 Day N sections, one-line warm-up, exactly 4 exercises with sets, reps and rest, one-line cooldown), plan rules, safety rules.
- User prompt (per request): selected goal, level, days, equipment, limitations.
- Training days are capped at 5, so at least 2 recovery days are always scheduled; the app never schedules more days than the user has available.
- No equipment means bodyweight only.
- Limitations apply to every part of the plan, including warm-ups and recovery days; vague limitations are not guessed at.
- The model is told not to diagnose or call any exercise safe.
- Injury text is wrapped in <<< >>> markers, length-limited to 300 characters, and treated as data, not instructions.
- The medical disclaimer box is shown by the app code whenever limitations are entered, instead of relying on the model.

## Error handling

| Input / failure | Result |
|---|---|
| Invalid or missing input | Yellow warning |
| Missing GROQ_API_KEY | Yellow warning |
| Bad key, rate limit, no internet, server error | Red message specific to the problem |
| Empty, cut-off, or incomplete (not Day 1 to 7) response | Yellow warning to try again |
| Any other unexpected error | Red generic message, no crash |

## Testing

Scenarios I ran with a real Groq key:
- No equipment, Advanced, 7 days, bad knees: 5 workout days and 2 rest days, upper-body bodyweight work with no bands, bikes or benches and no kneeling moves. One exercise (doorway pull-ups) still implied a bar.
- Full gym, 7 days, bad knees: upper-body exercises only, warm-ups limited to arm and shoulder mobility.
- Home dumbbells, 7 days, no limitation: no injury notice or blue box shown.
- Regenerate and Swap exercise: both worked with a real Groq key; swapping a name that is not in the plan shows a message without calling the API.
- Generate Plan is disabled while a current plan is showing and is enabled again when an input changes.
- Download as Markdown and as plain text both worked.

## Prompt iterations

1. Cut-off and reasoning_effort: openai/gpt-oss-20b is a reasoning model; thinking tokens count toward max_tokens. Fixed with reasoning_effort low and max_tokens 5000 (8000 was rejected with HTTP 413 on the free plan).
2. No equipment defined as bodyweight only.
3. Kneeling positions banned (bird dog, etc.).
4. Upper-body-only warm-ups for knee limitations.
5. Warm-ups under No equipment used an arm bike and a band: the equipment rule now applies to warm-ups and cooldowns, and an arm bike is allowed only with full gym access.
6. Equipment slips under No equipment (pull-up bar, band) kept changing between runs: the rule now lists the only allowed items (floor, wall, doorway, sturdy chair, sturdy table) instead of listing banned ones.

## Known limitations

- LLM output varies between runs, so rules are followed most of the time, not guaranteed; the app validates the Day 1 to 7 structure, not every exercise choice.
- With a vague limitation like bad knees, the plan avoids all lower-body work, so it may be less balanced.
- On Groq free plan, generating plans back to back can hit the per-minute token limit.
- Equipment and joint rules are enforced by the prompt only, so a rare slip (for example doorway pull-ups, which need a bar, under No equipment) can still occur; the app does not check exercise names.
- Regenerate and Swap each make another Groq request, so quick repeated clicks can hit the free-plan per-minute limit; Swap relies on the model to keep the rest of the plan unchanged, and the app only re-checks the Day 1 to 7 structure.

## Safety note

The generated plan is general information, not medical advice. Review the output carefully. For injuries or health limitations, consult a qualified health professional before following a plan.

Never upload `.env` or share your API key. `.env.example` contains placeholders and is safe to include in the repository.
