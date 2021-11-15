from logging import getLogger
from os import mkdir, path
from re import compile as re_compile
from uuid import uuid4

from requests import get
from requests.exceptions import ConnectionError, Timeout
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = ('txt', 'xml', 'md', 'mkd',)
DIR_MODE = 0o770
DRAFT_NAME = re_compile(r'(-\d+)?(\..*)?$')
DRAFT_NAME_WITH_REVISION = re_compile(r'\..*$')
OK = 200


# Exceptions
class DownloadError(Exception):
    '''Error class for download errors'''
    pass


def allowed_file(filename):
    '''Return true if file extension in allowed list'''

    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_extension(filename):
    '''Returns file extension'''
    _, file_ext = path.splitext(filename)
    return file_ext


def get_filename(filename, ext):
    '''Returns filename with given extension'''

    root, _ = path.splitext(filename)
    return '.'.join([root, ext])


def get_file(filename):
    '''Returns the filename part from a file path'''

    return filename.split('/')[-1]


def save_file(file, upload_dir):
    '''Save given file and returns path'''
    dir_path = path.join(upload_dir, str(uuid4()))
    mkdir(dir_path, mode=DIR_MODE)

    filename = path.join(
            dir_path,
            secure_filename(file.filename))
    file.save(filename)

    return (dir_path, filename)


def save_file_from_url(url, upload_dir, logger=getLogger()):
    '''Download and save the file from given URL and returns path'''
    dir_path = path.join(upload_dir, str(uuid4()))
    mkdir(dir_path, mode=DIR_MODE)
    filename = path.join(
            dir_path,
            secure_filename(url.split('/')[-1]))

    try:
        response = get(url)
    except (ConnectionError, Timeout) as e:
        logger.error('Connection error on {url}: {error}'.format(
                                                            url=url,
                                                            error=e))
        raise DownloadError('Error occured while downloading file.')

    if response.status_code == OK:
        with open(filename, 'w') as file:
            file.write(response.text)
    else:
        logger.error('Error downloading file: {}'.format(url))
        raise DownloadError('Error occured while downloading file.')

    return (dir_path, filename)


def get_name(filename):
    '''Returns draft/rfc name'''
    name = None

    if (
            filename.lower().startswith('draft-') or
            filename.lower().startswith('rfc')):
        name = DRAFT_NAME.sub('', filename.lower(), count=1)

    return name


def get_name_with_revision(filename):
    '''Retuns draft/rfc name with revision'''
    name = None

    if (
            filename.lower().startswith('draft-') or
            filename.lower().startswith('rfc')):
        name = DRAFT_NAME_WITH_REVISION.sub('', filename.lower(), count=1)

    return name
