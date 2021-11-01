from os import mkdir, path
from uuid import uuid4

from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = ('txt', 'xml', 'md', 'mkd')
ALLOWED_DIFF_EXTENSIONS = ('txt')
DIR_MODE = 0o770


def allowed_file(filename, diff=False):
    '''Return true if file extension in allowed list'''

    extensions = ALLOWED_DIFF_EXTENSIONS if diff else ALLOWED_EXTENSIONS

    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in extensions


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
