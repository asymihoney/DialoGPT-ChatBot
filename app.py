from flask import Flask, request, jsonify
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import sqlite3
import os

app = Flask(__name__)

# Load your model
model_path = ".\\text-gen-model"
tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
model = AutoModelForCausalLM.from_pretrained(model_path, local_files_only=True)

# Setup SQLite
DB_FILE = "chatlogs.db"

def init_db():
    if not os.path.exists(DB_FILE):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE chatlog (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_message TEXT NOT NULL,
                bot_reply TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

# Endpoint to chat with bot and save to database
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message")

    # Generate response
    prompt = f"User: {user_input}\nBot:"
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(**inputs, max_length=128, pad_token_id=tokenizer.eos_token_id)
    reply = tokenizer.decode(outputs[0], skip_special_tokens=True).split("Bot:")[-1].strip()

    # Save to DB
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chatlog (user_message, bot_reply) VALUES (?, ?)", (user_input, reply))
    conn.commit()
    conn.close()

    return jsonify({"reply": reply})

# Endpoint to fetch chat history
@app.route("/history", methods=["GET"])
def history():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT user_message, bot_reply FROM chatlog")
    chats = cursor.fetchall()
    conn.close()
    return jsonify(chats)

@app.route("/clear", methods=["POST"])
def clear_history():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chatlog")
    conn.commit()
    conn.close()
    return jsonify({"message": "Chat history cleared."})

if __name__ == "__main__":
    init_db()
    app.run(port=5000)
