from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

RASA_URL = "http://localhost:5005/webhooks/rest/webhook"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/send_message", methods=["POST"])
def send_message():
    message = request.json["message"]
    payload = {"sender": "user", "message": message}
    response = requests.post(RASA_URL, json=payload)
    
    messages = []
    for r in response.json():
        if "text" in r:
            messages.append(r["text"])
        if "image" in r:
            messages.append(f"<img src='{r['image']}' width='200'>")

    return jsonify({"messages": messages})

if __name__ == "__main__":
    app.run(debug=True)
