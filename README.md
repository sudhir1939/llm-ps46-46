# To-Do List from Text (LLM Mini Project, PS 46)

**Problem statement:** People write messy notes. This app converts free-text
notes into a prioritised to-do list with deadlines using an LLM (Gemini 2.5 Flash).

## Features
- Paste messy notes (or load sample notes)
- LLM returns tasks as JSON: `task`, `priority`, `deadline`
- Relative dates ("tomorrow", "Friday") resolved using today's date
- Tasks shown with a checkbox each, sorted by priority then deadline
- Download the list as CSV

## How to run
1. Get a free API key from https://aistudio.google.com/apikey
2. Copy `.env.example` to `.env` and put your key in it
3. Install and run:

```
pip install -r requirements.txt
streamlit run app.py
```

## Screenshots
<img width="1907" height="952" alt="image" src="https://github.com/user-attachments/assets/6b1894e7-ab91-4721-819d-fc2c1b087856" />
<img width="1907" height="949" alt="image" src="https://github.com/user-attachments/assets/e6d4a5fb-baae-4247-83c0-fcf64a54c45b" />

