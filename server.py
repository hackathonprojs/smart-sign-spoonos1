import os
import json
import asyncio
from flask import Flask, request, jsonify, send_from_directory, abort
from sequential_agents import SequentialFlowAgent

STATIC_DIR = os.getenv("STATIC_DIR", os.path.join(os.path.dirname(__file__), "static"))
app = Flask(__name__, static_folder=STATIC_DIR, static_url_path="/")

@app.get("/static/<path:filename>")
def serve_static(filename: str):
    try:
        return send_from_directory(STATIC_DIR, filename)
    except Exception:
        abort(404)

@app.get("/generate_doc")
def generate_doc():
    chat_json = request.args.get("chat_data")
    if chat_json:
        try:
            chat_data = json.loads(chat_json)
        except Exception:
            chat_data = []
    else:
        chat_data = [
            {"role": "user", "content": "I agree to sell the car for $8,000."},
            {"role": "assistant", "content": "Please confirm delivery timeline."},
            {"role": "user", "content": "Delivery within 7 days is fine."},
        ]
    passphrase = request.args.get("passphrase", "UltraSecure123")
    flow = SequentialFlowAgent()
    result = asyncio.run(flow.run(raw_messages=chat_data, encrypt_passphrase=passphrase))
    return jsonify(result)

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)