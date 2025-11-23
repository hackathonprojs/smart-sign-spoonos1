import os
import json
import asyncio
from flask import Flask, request, jsonify
from sequential_agents import SequentialFlowAgent

app = Flask(__name__)

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