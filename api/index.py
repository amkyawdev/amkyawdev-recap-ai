from openrouter import handler

# Export for Vercel Python Runtime
def index(request):
    """Vercel Python Function Entry Point"""
    return handler({
        "method": request.method,
        "path": request.path,
        "body": request.get_data(as_text=True) or "{}",
        "headers": dict(request.headers),
    })
