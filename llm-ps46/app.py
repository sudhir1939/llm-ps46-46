"""PS 46 - To-Do List from Text.

Paste messy free-text notes, and an LLM (Gemini) turns them into a
prioritised to-do list with deadlines. Tasks are shown with checkboxes
and sorted by priority.
"""
import json
import os
from datetime import date

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

MODEL = "gemini-3.5-flash-lite"
PRIORITY_RANK = {"High": 0, "Medium": 1, "Low": 2}
PRIORITY_ICON = {"High": "🔴", "Medium": "🟠", "Low": "🟢"}

SAMPLE_NOTES = (
    "Need to submit the LLM mini project by Sunday 11:30 am. Also call mom "
    "sometime this week. Pay the hostel fee before 30 Nov, it's urgent. "
    "Maybe watch the new ML lecture when free. Buy a notebook tomorrow. "
    "Prepare for the DBMS viva on Wednesday."
)

PROMPT_TEMPLATE = """You are a task-extraction assistant.
Today's date is {today} ({weekday}).

Read the messy notes below and convert them into a to-do list.
Rules:
1. Return ONLY a JSON array. Each item must have exactly these keys:
   "task"     : short action phrase (max 10 words), starting with a verb
   "priority" : one of "High", "Medium", "Low"
   "deadline" : date as YYYY-MM-DD, or "None" if no deadline is mentioned
2. Resolve relative dates (tomorrow, Friday, next week) using today's date.
3. Use High for urgent / near deadlines or words like urgent, ASAP, important;
   Low for optional things ("maybe", "when free"); otherwise Medium.
4. Do not invent tasks that are not in the notes. One task per action.

NOTES:
\"\"\"{notes}\"\"\"
"""


def get_client():
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        st.error("GEMINI_API_KEY not found. Add it to a .env file (see README).")
        st.stop()
    if "genai_client" not in st.session_state:
        st.session_state.genai_client = genai.Client(api_key=key)
    return st.session_state.genai_client


def extract_tasks(notes: str) -> list[dict]:
    """Call the LLM and return a cleaned list of task dicts."""
    today = date.today()
    prompt = PROMPT_TEMPLATE.format(
        today=today.isoformat(), weekday=today.strftime("%A"), notes=notes
    )
    response = get_client().models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json", temperature=0.2
        ),
    )
    return clean_tasks(json.loads(response.text))


def clean_tasks(raw) -> list[dict]:
    """Validate the LLM output and sort by priority, then deadline."""
    if isinstance(raw, dict):  # model sometimes wraps the list in an object
        raw = next((v for v in raw.values() if isinstance(v, list)), [])
    tasks = []
    for item in raw:
        if not isinstance(item, dict) or not item.get("task"):
            continue
        priority = str(item.get("priority", "Medium")).capitalize()
        if priority not in PRIORITY_RANK:
            priority = "Medium"
        deadline = str(item.get("deadline", "None") or "None")
        tasks.append({"task": str(item["task"]).strip(),
                      "priority": priority, "deadline": deadline})
    tasks.sort(key=lambda t: (PRIORITY_RANK[t["priority"]],
                              t["deadline"] == "None", t["deadline"]))
    return tasks


def main():
    st.set_page_config(page_title="To-Do List from Text", page_icon="✅")
    st.title("✅ To-Do List from Text")
    st.caption("Paste messy notes → get a prioritised to-do list with deadlines.")

    if "notes" not in st.session_state:
        st.session_state.notes = ""
    if st.button("Load sample notes"):
        st.session_state.notes = SAMPLE_NOTES

    notes = st.text_area("Your notes", key="notes", height=180,
                         placeholder="e.g. call dentist tomorrow, finish report by Friday...")

    if st.button("Create to-do list", type="primary"):
        if not notes.strip():
            st.warning("Please enter some notes first.")
        else:
            with st.spinner("Reading your notes..."):
                try:
                    st.session_state.tasks = extract_tasks(notes)
                except Exception as exc:  # bad JSON, quota, network...
                    st.error(f"Could not create the list: {exc}")

    tasks = st.session_state.get("tasks", [])
    if tasks:
        st.subheader(f"Your tasks ({len(tasks)})")
        for i, t in enumerate(tasks):
            label = f"{PRIORITY_ICON[t['priority']]} **{t['task']}**  —  {t['priority']}"
            if t["deadline"] != "None":
                label += f"  ·  due {t['deadline']}"
            st.checkbox(label, key=f"task_{i}")
        st.download_button("Download as CSV",
                           pd.DataFrame(tasks).to_csv(index=False),
                           file_name="todo_list.csv", mime="text/csv")


if __name__ == "__main__":
    main()
