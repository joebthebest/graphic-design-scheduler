class VercelPathFixMiddleware:
    """
    Middleware to normalize Vercel serverless function URLs so /api/index.py
    is stripped and routes match standard Django endpoints seamlessly.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        for prefix in ['/api/index.py', 'api/index.py', '/api/index', 'api/index']:
            if request.path_info.startswith(prefix):
                cleaned = request.path_info[len(prefix):]
                request.path_info = cleaned if cleaned.startswith('/') else ('/' + cleaned)
                request.path = request.path_info
                break
        return self.get_response(request)
