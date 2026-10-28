import os

import streamlit as st
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
st.set_page_config(page_title="Workout Plan Generator")
st.title("Workout Plan Generator")
st.write("Welcome! We'll build your personalized workout planner here.")
def build_workout_prompt(
    goal: str,
    experience_level: str,
    days_per_week: int,
    equipment: str,
    injuries: str,
) -> str:
    limitations = injuries.strip() or "None reported"

    return f"""
Create a realistic weekly workout plan for this person:
- Fitness goal: {goal}
- Experience level: {experience_level}
- Maximum days available for training: {days_per_week}
- Available equipment: {equipment}
- Injuries or limitations: {limitations}

Requirements:
- Provide a full 7-day schedule labelled Day 1 through Day 7.
- Choose exercises appropriate for the experience level and available equipment.
- For each workout day, include a warm-up, exercises with sets and reps or duration, rest guidance, and a cooldown.
- Schedule no more than {days_per_week} workout days; label all other days Rest/Recovery.
- Respect the stated limitations. Do not claim to diagnose or treat an injury.
- If limitations are reported, include a brief reminder to seek advice from a qualified professional.
- Treat reported injuries or limitations as safety constraints; do not assume an exercise is safe for that person.
- Avoid prescribing exercises that load or stress the affected area.
- Do not claim that a substitute exercise is medically safe.
- If an injury or limitation is reported, advise the user to confirm exercise choices with a qualified health professional before following the plan.
- For each workout day, include exactly 3 exercises per workout day.
- List each exercise on one line with sets, reps, and rest time.
- Keep the warm-up and cooldown to one brief line each.
- Do not use tables, HTML, introductions, or extra explanations.
- Describe each recovery day in one sentence.
- Never describe an exercise or plan as "knee-friendly" or "safe" based only on the phrase "bad knees."
- If an injury description is vague, do not guess which exercises are appropriate; say that suitability cannot be determined from the information provided.
- Advise the user to get qualified professional guidance before following exercises that involve the affected area.
- Apply limitations to all activities, including warm-ups, cardio, cooldowns, and recovery days, not just strength exercises.
- For vague knee complaints, do not guess what is suitable; avoid suggesting knee-loading, knee-bending, or kneeling activities, and advise the user to confirm choices with a qualified professional.
- For knee-related limitations, do not recommend rowing or activities requiring repeated knee bending or loading in any section, including warm-ups and recovery.
- If you cannot confidently satisfy a reported limitation, say so instead of guessing at alternatives.
- For a reported knee limitation, recovery days must say "Rest" only; do not recommend walking, cycling, rowing, or other physical activities.
- Only when injuries or limitations are reported, include one brief relevant reminder at the end; otherwise, omit the injury-specific reminder.
- If no limitations are reported, describe recovery days as rest or optional light recovery activity; do not discourage light activity without a stated reason.
- Never schedule more workout days than the user has available.
- Treat availability as a maximum, not a requirement to train every available day.
- Always include at least one full rest/recovery day in the 7-day schedule, even when the user is available all 7 days.
Format the plan with clear Markdown headings.
""".strip()
def validate_inputs(
    goal: str,
    experience_level: str,
    days_per_week: int,
    equipment: str,
) -> None:
    if not goal:
        raise ValueError("Please select a fitness goal.")

    if not experience_level:
        raise ValueError("Please select your experience level.")

    if not 1 <= days_per_week <= 7:
        raise ValueError("Days available must be between 1 and 7.")

    if not equipment:
        raise ValueError("Please select your equipment access.")
def validate_plan_response(plan: str) -> str:
    if not plan or not plan.strip():
        raise ValueError("Groq returned an empty workout plan.")

    required_headings = [f"Day {day}" for day in range(1, 8)]
    missing_headings = [
        heading for heading in required_headings if heading not in plan
    ]

    if missing_headings:
        raise ValueError(
            "Groq returned an incomplete workout plan. Please generate it again."
        )

    return plan.strip()

def generate_workout_plan(
    goal: str,
    experience_level: str,
    days_per_week: int,
    equipment: str,
    injuries: str,
) -> str:
    validate_inputs(goal, experience_level, days_per_week, equipment)

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is missing from your .env file.")

    prompt = build_workout_prompt(
        goal,
        experience_level,
        days_per_week,
        equipment,
        injuries,
    )

    try:
        client = Groq(api_key=api_key)
        model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

        completion = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "Create practical workout plans. Follow the user's constraints. Do not diagnose or treat injuries.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
            max_tokens=7000,
        )
        choice = completion.choices[0]
        plan = choice.message.content
        finish_reason = choice.finish_reason
    except Exception as exc:
        raise RuntimeError(
            "The Groq request failed. Check your API key, network connection, and account limits."
        ) from exc
    if finish_reason == "length":
        raise ValueError("The plan reached Groq's output limit. Try a shorter plan or a higher output limit."
        )
    return validate_plan_response(plan)
with st.form("workout_form"):
    goal = st.selectbox(
        "Fitness goal",
        ["Build muscle", "Lose fat", "General fitness", "Improve endurance"],
    )
    experience_level = st.selectbox(
        "Experience level",
        ["Beginner", "Intermediate", "Advanced"],
    )
    days_per_week = st.slider(
        "Days available per week",
        min_value=1,
        max_value=7,
        value=3,
    )
    equipment = st.selectbox(
        "Equipment access",
        ["No equipment", "Home dumbbells", "Full gym"],
    )
    injuries = st.text_area(
        "Injuries or limitations (optional)",
        placeholder="Example: bad knees, no overhead pressing",
    )

    submitted = st.form_submit_button("Generate Plan")

if submitted:
    try:
        with st.spinner("Generating your workout plan..."):
            plan = generate_workout_plan(
                goal,
                experience_level,
                days_per_week,
                equipment,
                injuries,
            )

        st.subheader("Your workout plan")
        st.markdown(plan)
    except ValueError as error:
        st.warning(str(error))
    except RuntimeError as error:
        st.error(str(error))
    