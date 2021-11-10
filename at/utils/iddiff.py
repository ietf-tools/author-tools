from logging import getLogger
from subprocess import run as proc_run, CalledProcessError

from requests import get


OK = 200


# Exceptions
class IddiffError(Exception):
    '''Error class for iddiff errors'''
    pass


class LatestDraftNotFound(Exception):
    '''Error class for latest draft not found error'''
    pass


def get_id_diff(filename_1, filename_2, logger=getLogger()):
    '''Returns iddiff output'''

    logger.debug('running iddiff')

    output = proc_run(
                args=['iddiff', filename_1, filename_2], capture_output=True)

    try:
        output.check_returncode()
    except CalledProcessError:
        logger.info('iddiff error: {}:'.format(output.stderr.decode('utf-8')))
        raise IddiffError(output.stderr.decode('utf-8'))

    return output.stdout.decode('utf-8')


def get_latest(draft, dt_latest_url, logger=getLogger()):
    '''Returns URL latest ID/RFC from Datatracker.'''

    url = '/'.join([dt_latest_url, draft])
    response = get(url)

    if response.status_code == OK:
        try:
            latest_draft = response.json()['content_url']
        except KeyError:
            logger.error('can not find content_url for {}'.format(url))
            raise LatestDraftNotFound(
                    'Can not find url for the latest draft on datatracker')
    else:
        logger.error('can not find draft for {}'.format(url))
        raise LatestDraftNotFound(
                'Can not find the latest draft on datatracker')

    return latest_draft
