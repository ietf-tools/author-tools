from decorator import decorator
from flask import current_app, jsonify, request
from requests import post

UNAUTHORIZED = 401
OK = 200


@decorator
def require_api_key(f, *args, **kwargs):
    '''Returns the function if api authentication passes.
    Else returns JSON reponse with an error.'''
    logger = current_app.logger
    config = current_app.config

    if not config['REQUIRE_AUTH']:
        logger.debug('Datatracker authentication is not required')
    else:
        apikey = request.headers.get('X-API-KEY')
        if apikey is None or apikey.strip() == '':
            if 'apikey' in request.form.keys():
                apikey = request.form['apikey']
            else:
                logger.error('missing api key')
                return jsonify(error='API key is missing'), UNAUTHORIZED

        with post(config['DT_APPAUTH_URL'],
                  data={'apikey': apikey.strip()}) as response:
            if (response.status_code == OK and
                    response.json()['success'] is True):
                logger.debug('valid apikey')
            else:
                logger.error('invalid api key')
                return jsonify(error='API key is invalid'), UNAUTHORIZED

    return f(*args, **kwargs)
