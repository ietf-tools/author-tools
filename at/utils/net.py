from logging import getLogger
from urllib.parse import urlsplit

from requests import get


OK = 200
ALLOWED_SCHEMES = ['http', 'https']


# Exceptions
class DocumentNotFound(Exception):
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


def get_latest(doc, dt_latest_url, logger=getLogger()):
    '''Returns URL latest ID/RFC from Datatracker.'''

    url = '/'.join([dt_latest_url, doc])
    response = get(url)

    if response.status_code == OK:
        try:
            data = response.json()
            latest_doc = data['content_url']
        except KeyError:
            logger.error('can not find content_url for {}'.format(url))
            raise DocumentNotFound(
                    'Can not find url for the latest document on datatracker')
    else:
        logger.error('can not find doc for {}'.format(url))
        raise DocumentNotFound(
                'Can not find the latest document on datatracker')

    return latest_doc


def get_previous(doc, dt_latest_url, logger=getLogger()):
    '''Returns previous ID/RFC from datatracker'''
    url = '/'.join([dt_latest_url, doc])
    response = get(url)

    if response.status_code == OK:
        try:
            data = response.json()
            previous_doc = data['previous']
        except KeyError:
            logger.error('can not find content_url for {}'.format(url))
            raise DocumentNotFound(
                'Can not find url for the previous document on datatracker')
    else:
        logger.error('can not find doc for {}'.format(url))
        raise DocumentNotFound(
                'Can not find the previous document on datatracker')

    return get_latest(previous_doc, dt_latest_url, logger)


def get_both(doc, dt_latest_url, logger=getLogger()):
    '''Returns urls of given doc  and previous ID/RFC from Datatracker.'''

    url = '/'.join([dt_latest_url, doc])
    response = get(url)

    if response.status_code == OK:
        try:
            data = response.json()
            latest_doc = data['content_url']
            try:
                previous_doc = data['previous_url']
            except KeyError:
                logger.error('Can not find previous_url for {}'.format(url))
                raise DocumentNotFound(
                    'Can not find url for previous document on datatracker')
        except KeyError:
            logger.error('can not find content_url for {}'.format(url))
            raise DocumentNotFound(
                    'Can not find url for the latest document on datatracker')
    else:
        logger.error('can not find doc for {}'.format(url))
        raise DocumentNotFound(
                'Can not find the latest document on datatracker')

    return (previous_doc, latest_doc)


def is_url(string):
    '''Returns True if string is an URL'''
    try:
        url_parts = urlsplit(string)
        return all([url_parts.scheme, url_parts.netloc])
    except ValueError:
        return False
