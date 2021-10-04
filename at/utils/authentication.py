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

    if 'apikey' in request.form.keys():
        response = post(
                    config['DT_APPAUTH_URL'],
                    data={'apikey': request.form['apikey']})
        if response.status_code == OK and response.json()['success'] is True:
            logger.debug('valid apikey')
        else:
            logger.error('invalid api key')
            return jsonify(error='API key is invalid'), UNAUTHORIZED
    else:
        logger.error('missing api key')
        return jsonify(error='API key is missing'), UNAUTHORIZED

    return f(*args, **kwargs)
