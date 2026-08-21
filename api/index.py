import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'graphic_design_scheduler.settings')

_application = get_wsgi_application()

def app(environ, start_response):
    # 1. Retrieve the actual requested URL path from Vercel headers
    matched_path = (
        environ.get('HTTP_X_MATCHED_PATH') or 
        environ.get('HTTP_X_FORWARDED_URI') or 
        environ.get('HTTP_X_VERCEL_PATH') or 
        environ.get('PATH_INFO', '/')
    )
    
    # Strip query string if present
    if '?' in matched_path:
        matched_path = matched_path.split('?')[0]

    # Strip /api/index.py or /api/index prefix if present
    for prefix in ['/api/index.py', 'api/index.py', '/api/index', 'api/index']:
        if matched_path.startswith(prefix):
            matched_path = matched_path[len(prefix):] or '/'
            break

    if not matched_path.startswith('/'):
        matched_path = '/' + matched_path

    environ['PATH_INFO'] = matched_path
    environ['REQUEST_URI'] = matched_path
    environ['RAW_URI'] = matched_path

    return _application(environ, start_response)
