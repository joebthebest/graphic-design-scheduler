class VercelPathFixMiddleware:
    """
    Middleware to ensure the actual requested route is used for Django URL resolution
    when deployed behind Vercel serverless rewrites.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        real_path = (
            request.META.get('HTTP_X_MATCHED_PATH') or 
            request.META.get('HTTP_X_FORWARDED_URI') or 
            request.META.get('HTTP_X_VERCEL_PATH')
        )
        if real_path:
            if '?' in real_path:
                real_path = real_path.split('?')[0]
            for prefix in ['/api/index.py', 'api/index.py', '/api/index', 'api/index']:
                if real_path.startswith(prefix):
                    real_path = real_path[len(prefix):] or '/'
                    break
            if not real_path.startswith('/'):
                real_path = '/' + real_path
            request.path_info = real_path
            request.path = real_path
        else:
            for prefix in ['/api/index.py', 'api/index.py', '/api/index', 'api/index']:
                if request.path_info.startswith(prefix):
                    cleaned = request.path_info[len(prefix):]
                    request.path_info = cleaned if cleaned.startswith('/') else ('/' + cleaned)
                    request.path = request.path_info
                    break
        return self.get_response(request)
