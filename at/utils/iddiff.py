from logging import getLogger
from subprocess import run as proc_run, CalledProcessError
from urllib.parse import urlsplit

from requests import get

from at.utils.file import get_extension, save_file, save_file_from_url
from at.utils.processor import (
        get_text, get_xml, md2xml, KramdownError, MmarkError, XML2RFCError)


OK = 200
ALLOWED_SCHEMES = ['http', 'https']


# Exceptions
class IddiffError(Exception):
    '''Error class for iddiff errors'''
    pass


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


def get_id_diff(old_draft, new_draft, table=False, wdiff=False,
                logger=getLogger()):
    '''Returns iddiff output'''

    logger.debug('running iddiff')

    if wdiff:
        output = proc_run(args=['iddiff', '-w', old_draft, new_draft],
                          capture_output=True)
    elif table:
        output = proc_run(args=['iddiff', '-t', '-c', old_draft, new_draft],
                          capture_output=True)
    else:
        output = proc_run(args=['iddiff', '-c', old_draft, new_draft],
                          capture_output=True)

    try:
        output.check_returncode()
    except CalledProcessError:
        logger.info('iddiff error: {}:'.format(output.stderr.decode('utf-8')))
        raise IddiffError(output.stderr.decode('utf-8'))

    return output.stdout.decode('utf-8')


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


def get_text_id_from_file(file, upload_dir, logger=getLogger()):
    '''Save file and returns text draft'''

    (dir_path, filename) = save_file(file, upload_dir)

    return get_text_id(dir_path, filename, logger)


def get_text_id_from_url(url, upload_dir, logger=getLogger()):
    '''Save file from URL and returns text draft'''

    (dir_path, filename) = save_file_from_url(url, upload_dir)

    return get_text_id(dir_path, filename, logger)


def get_text_id(dir_path, filename, logger=getLogger()):
    '''Returns text draft'''
    file_ext = get_extension(filename)

    if file_ext.lower() != '.txt':
        logger.debug('processing non text file')

        try:
            if file_ext.lower() in ['.md', '.mkd']:
                filename = md2xml(filename, logger)
            xml_file = get_xml(filename, logger=logger)
            filename = get_text(xml_file, logger=logger)
        except (KramdownError, MmarkError, XML2RFCError) as e:
            logger.error(
                    'error processing non text file: {}'.format(filename))
            raise IddiffError(str(e))

    return (dir_path, filename)
