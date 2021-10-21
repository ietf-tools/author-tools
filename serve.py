from logging import getLogger, INFO
from waitress import serve
from at import create_app

for log in ['waitress', 'at']:
    logger = getLogger(log)
    logger.setLevel(INFO)
app = create_app()
serve(app, listen='*:80')
