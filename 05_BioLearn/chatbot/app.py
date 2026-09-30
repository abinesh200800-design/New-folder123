import os
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from google import genai
from chatbot_config import BOT_NAME, SYSTEM_PROMPT

load_dotenv(override=True)

app = Flask(__name__)

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY is missing from the .env file.")

client = genai.Client(api_key=api_key)
MODEL_NAME = "gemini-3.1-flash-lite"

@app.get("/")
def home():
    return render_template("index.html", bot_name=BOT_NAME)

@app.post("/chat")
def chat():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()

    if not message:
        return jsonify({"error": "Please enter a question."}), 400

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=message,
            config={
                "system_instruction": SYSTEM_PROMPT,
                "thinking_config": {"thinking_level": "minimal"},
            },
        )
        reply = (response.text or "").strip()
        if not reply:
            reply = "I could not generate a response. Please try again."
        return jsonify({"reply": reply, "bot_name": BOT_NAME})
    except Exception:
        return jsonify({
            "error": "The chatbot could not process your request right now."
        }), 500

if __name__ == "__main__":
    app.run()
