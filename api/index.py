import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'graphic_design_scheduler.settings')

_application = get_wsgi_application()

def app(environ, start_response):
    for key in ['PATH_INFO', 'REQUEST_URI', 'RAW_URI']:
        if key in environ and environ[key]:
            for prefix in ['/api/index.py', 'api/index.py', '/api/index', 'api/index']:
                if environ[key].startswith(prefix):
                    cleaned = environ[key][len(prefix):]
                    environ[key] = cleaned if cleaned.startswith('/') else ('/' + cleaned)
                    break
    return _application(environ, start_response)
