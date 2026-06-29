import json

def index(request):
    """Vercel Python Runtime Handler"""
    method = request.method
    
    # CORS headers
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
    }
    
    # Handle preflight
    if method == "OPTIONS":
        return {"statusCode": 200, "headers": headers, "body": ""}
    
    # Return success response
    return {
        "statusCode": 200,
        "headers": {**headers, "Content-Type": "application/json"},
        "body": json.dumps({"status": "ok", "message": "Recap AI API"})
    }
