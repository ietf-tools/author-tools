import os

accesslog = "-"
errorlog = "-"
capture_output = True
control_socket_disable = True
workers = os.getenv("GUNICORN_WORKERS", 2)
worker_class = "gevent"
bind = "0.0.0.0:8008"
