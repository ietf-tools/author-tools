from logging import getLogger
from subprocess import run as proc_run, CalledProcessError

from requests import get

from at.utils.file import get_extension, save_file
from at.utils.processor import (
        get_text, get_xml, md2xml, KramdownError, MmarkError, XML2RFCError)


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


def get_text_id(file, upload_dir, logger=getLogger()):
    '''Returns text draft'''

    (dir_path, filename) = save_file(file, upload_dir)
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
