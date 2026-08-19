import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'graphic_design_scheduler.settings')

_application = get_wsgi_application()

def app(environ, start_response):
    path = environ.get('PATH_INFO', '')
    if path.startswith('/api/index.py'):
        environ['PATH_INFO'] = path.replace('/api/index.py', '', 1) or '/'
    elif path.startswith('/api/index'):
        environ['PATH_INFO'] = path.replace('/api/index', '', 1) or '/'
    return _application(environ, start_response)
