class VercelPathFixMiddleware:
    """
    Middleware to ensure clean Django URL resolution on Vercel.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        for prefix in [
            '/graphic_design_scheduler/wsgi.py',
            'graphic_design_scheduler/wsgi.py',
            '/api/index.py',
            'api/index.py',
            '/api/index',
            'api/index',
            '/api',
        ]:
            if request.path_info.startswith(prefix):
                cleaned = request.path_info[len(prefix):]
                request.path_info = cleaned if cleaned.startswith('/') else ('/' + cleaned)
                request.path = request.path_info
                break
        return self.get_response(request)
