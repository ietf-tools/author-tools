from logging import getLogger

from at.utils.file import get_extension, save_file, save_file_from_url
from at.utils.processor import (
    get_text,
    get_xml,
    md2xml,
    rst2xml,
    ProcessingError,
)


# Exceptions
class TextProcessingError(Exception):
    """Error class for text errors"""

    pass


def get_text_id_from_file(
    file, upload_dir, raw=False, text_or_xml=False, logger=getLogger()
):
    """Save file and returns text draft"""

    dir_path, filename = save_file(file, upload_dir)

    if not raw:
        file_ext = get_extension(filename).lower()
        if not text_or_xml or (text_or_xml and file_ext not in [".txt", ".xml"]):
            dir_path, filename = get_text_id(dir_path, filename, logger)

    return (dir_path, filename)


def get_text_id_from_url(
    url, upload_dir, raw=False, text_or_xml=False, logger=getLogger()
):
    """Save file from URL and returns text draft"""

    dir_path, filename = save_file_from_url(url, upload_dir)

    if not raw:
        file_ext = get_extension(filename).lower()
        if not text_or_xml or (text_or_xml and file_ext not in [".txt", ".xml"]):
            dir_path, filename = get_text_id(dir_path, filename, logger)

    return (dir_path, filename)


def get_text_id(dir_path, filename, logger=getLogger()):
    """Returns text draft"""
    file_ext = get_extension(filename)

    if file_ext.lower() != ".txt":
        logger.debug("processing non text file")

        try:
            if file_ext.lower() in [".md", ".mkd"]:
                filename = md2xml(filename, logger)
            elif file_ext.lower() in [".rst"]:
                filename = rst2xml(filename, logger)
            xml_file, _ = get_xml(filename, logger=logger)
            filename, _ = get_text(xml_file, logger=logger)
        except ProcessingError as e:
            logger.error("error processing non text file: {}".format(filename))
            raise TextProcessingError(str(e))

    return (dir_path, filename)
