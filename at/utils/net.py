from logging import getLogger
from urllib.parse import urlsplit

from requests import get


OK = 200
ALLOWED_SCHEMES = ['http', 'https']


# Exceptions
class LatestDraftNotFound(Exception):
    '''Error class for latest draft not found error'''
    pass


class InvalidURL(Exception):
    '''Error class for invalid URLs'''
    pass


def is_valid_url(url, allowed_domains=None, logger=getLogger()):
    '''Checks if provided URL is valid and allowed URL'''

    try:
        url_parts = urlsplit(url)
        if url_parts.scheme not in ALLOWED_SCHEMES:
            logger.info('URL: {} scheme is not allowed.')
            raise InvalidURL('{} scheme is not allowed.'.format(
                url_parts.scheme))
        if '.'.join(url_parts.netloc.split('.')[-2:]) not in allowed_domains:
            logger.info('URL: {} domain is not allowed.')
            raise InvalidURL('{} domain is not allowed.'.format(
                url_parts.netloc))
    except ValueError as e:
        logger.info('invalid URL: {url} error: {error}'.format(
            url=url, error=str(e)))
        raise InvalidURL('Invalid URL: {}'.format(url))

    return True


def get_latest(draft, dt_latest_url, original_draft=None, logger=getLogger()):
    '''Returns URL latest ID/RFC from Datatracker.'''

    url = '/'.join([dt_latest_url, draft])
    response = get(url)

    if response.status_code == OK:
        try:
            data = response.json()
            latest_draft = data['content_url']

            if original_draft:
                draft_name = data['name']
                if 'rev' in data.keys():
                    draft_name = '-'.join([data['name'], data['rev']])

                if draft_name == original_draft:
                    latest_draft = get_latest(draft=data['previous'],
                                              dt_latest_url=dt_latest_url,
                                              logger=logger)

        except KeyError:
            logger.error('can not find content_url for {}'.format(url))
            raise LatestDraftNotFound(
                    'Can not find url for the latest draft on datatracker')
    else:
        logger.error('can not find draft for {}'.format(url))
        raise LatestDraftNotFound(
                'Can not find the latest draft on datatracker')

    return latest_draft
