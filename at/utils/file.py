from logging import getLogger
from os import mkdir, path
from re import compile as re_compile
from uuid import uuid4

from decorator import decorator
from flask import current_app, jsonify, request
from requests import get
from requests.exceptions import ConnectionError, Timeout
from werkzeug.utils import secure_filename


ALLOWED_EXTENSIONS = (
    "txt",
    "xml",
    "md",
    "mkd",
)
ALLOWED_EXTENSIONS_BY_PROCESS = {
    "svgcheck": ("svg",),
    "clean_svg_ids": ("xml",),
}
DIR_MODE = 0o770
DRAFT_NAME = re_compile(r"(-\d+)?(\..*)?$")
DRAFT_NAME_WITH_REVISION = re_compile(r"\..*$")
OK = 200
BAD_REQUEST = 400


# Exceptions
class DownloadError(Exception):
    """Error class for download errors"""

    pass


def allowed_file(filename, process=None):
    """Return true if file extension in allowed list"""

    if "." in filename:
        ext = filename.rsplit(".", 1)[1].lower()
        if process:
            return ext in ALLOWED_EXTENSIONS_BY_PROCESS[process]
        else:
            return ext in ALLOWED_EXTENSIONS
    else:
        return False


def get_extension(filename):
    """Returns file extension"""
    _, file_ext = path.splitext(filename)
    return file_ext


def get_filename(filename, ext):
    """Returns filename with given extension"""

    root, _ = path.splitext(filename)
    return ".".join([root, ext])


def get_file(filename):
    """Returns the filename and the parent directory"""

    return "/".join(filename.split("/")[-2:])


def save_file(file, upload_dir):
    """Save given file and returns path"""
    dir_path = path.join(upload_dir, str(uuid4()))
    mkdir(dir_path, mode=DIR_MODE)

    filename = path.join(dir_path, secure_filename(file.filename))
    file.save(filename)

    return (dir_path, filename)


def save_file_from_text(text, upload_dir):
    """Save given text to file and returns path"""
    dir_path = path.join(upload_dir, str(uuid4()))
    mkdir(dir_path, mode=DIR_MODE)

    filename = path.join(dir_path, secure_filename(".".join([str(uuid4()), "txt"])))

    with open(filename, "w") as file:
        file.write(text)

    return (dir_path, filename)


def save_file_from_url(url, upload_dir, logger=getLogger()):
    """Download and save the file from given URL and returns path"""
    dir_path = path.join(upload_dir, str(uuid4()))
    mkdir(dir_path, mode=DIR_MODE)
    save_filename = secure_filename(url.split("/")[-1])
    if len(save_filename) == 0:
        error = "Can not determine the filename: {}".format(url)
        logger.error(error)
        raise DownloadError(error)
    filename = path.join(dir_path, save_filename)

    try:
        with get(url) as response:
            if response.status_code == OK:
                with open(filename, "w") as file:
                    file.write(response.text)
            else:
                logger.error("Error downloading file: {}".format(url))
                raise DownloadError("Error occured while downloading file.")

        return (dir_path, filename)
    except (ConnectionError, Timeout) as e:
        logger.error("Connection error on {url}: {error}".format(url=url, error=e))
        raise DownloadError("Error occured while downloading file.")


def get_name(filename):
    """Returns draft/rfc name"""
    name = None

    if filename.lower().startswith("draft-") or filename.lower().startswith("rfc"):
        name = DRAFT_NAME.sub("", filename.lower(), count=1)

    return name


def get_name_with_revision(filename):
    """Retuns draft/rfc name with revision"""
    name = None

    if filename.lower().startswith("draft-") or filename.lower().startswith("rfc"):
        name = DRAFT_NAME_WITH_REVISION.sub("", filename.lower(), count=1)

    return name


def cleanup_output(filename, output):
    """Return output without directory information"""

    if output:
        return output.replace(path.dirname(filename) + "/", "").replace(
            path.dirname(path.relpath(filename)) + "/", ""
        )
    else:
        return None


@decorator
def check_file(f, *args, **kwargs):
    """Check posted files"""
    logger = current_app.logger

    file_check_process = None
    if "/svgcheck" in request.path:
        file_check_process = "svgcheck"
    if "/clean_svg_ids" in request.path:
        file_check_process = "clean_svg_ids"

    for file_entry in request.files:
        file = request.files[file_entry]

        if file.filename == "":
            logger.info("filename missing")
            return jsonify(error="Filename is missing"), BAD_REQUEST
        if not allowed_file(file.filename, process=file_check_process):
            logger.info("File format not supportted: {}".format(file.filename))
            return jsonify(error="Input file format not supported"), BAD_REQUEST

    return f(*args, **kwargs)
