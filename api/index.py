import json

# Simple API endpoint
def index(request):
    return json.dumps({"status": "ok", "message": "Recap AI API"})
