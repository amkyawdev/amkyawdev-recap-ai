from flask import Flask, request, jsonify
from openrouter import handler

app = Flask(__name__)

@app.route("/api/openrouter", defaults={"path": ""}, methods=["GET", "POST", "OPTIONS"])
@app.route("/api/openrouter/<path:path>", methods=["GET", "POST", "OPTIONS"])
def vercel_handler(path):
    event = {
        "method": request.method,
        "path": request.path,
        "body": request.get_data(as_text=True) or "{}",
        "headers": dict(request.headers),
    }
    response = handler(event)
    return jsonify(response.get("body", {})), response.get("statusCode", 200)
