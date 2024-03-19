import os

accesslog = '-'
errorlog = '-'
capture_output = True
workers = os.getenv('GUNICORN_WORKERS', 2)
worker_class = 'eventlet'
bind = '0.0.0.0:8008'
