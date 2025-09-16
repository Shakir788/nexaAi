# Nexa — Streamlit Study Buddy (Prototype)

This prototype Streamlit app is a starting point for *Nexa*, the AI study buddy you built.
It includes image upload + basic OCR fallback, text summarization, quiz generation, flashcards,
user profile, simple Pomodoro timer UI, and safe OpenAI API usage patterns (API key from environment).

## Quick start (locally)
1. Create and activate a virtual environment
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set environment variable `OPENAI_API_KEY` (do **not** hard-code keys):
   ```bash
   export OPENAI_API_KEY='sk-...'
   ```
   On Windows (PowerShell):
   ```powershell
   $env:OPENAI_API_KEY = 'sk-...'
   ```
4. Run the app:
   ```bash
   streamlit run app.py
   ```

## Notes
- The app expects an OpenAI-compatible key. Keep it server-side and never expose in a client bundle.
- Image OCR uses `pytesseract` if installed and tesseract binary is available. Otherwise, image bytes are sent to the model as a fallback (may cost more).
