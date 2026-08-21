import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'graphic_design_scheduler.settings')

_application = get_wsgi_application()

def app(environ, start_response):
    for prefix in [
        '/graphic_design_scheduler/wsgi.py',
        'graphic_design_scheduler/wsgi.py',
        '/api/index.py',
        'api/index.py',
        '/api/index',
        'api/index',
        '/api',
    ]:
        if 'PATH_INFO' in environ and environ['PATH_INFO'].startswith(prefix):
            cleaned = environ['PATH_INFO'][len(prefix):]
            environ['PATH_INFO'] = cleaned if cleaned.startswith('/') else ('/' + cleaned)
            break
    return _application(environ, start_response)
