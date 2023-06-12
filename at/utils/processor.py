from logging import getLogger
from subprocess import run as proc_run, CalledProcessError

from xml2rfc import XmlRfcParser
from xml2rfc.parser import XmlRfcError
from lxml.etree import XMLSyntaxError

from at.utils.file import get_extension, get_filename, save_file
from at.utils.logs import get_errors, process_xml2rfc_log


# Exceptions
class XML2RFCError(Exception):
    '''Error class for xml2rfc errors'''
    pass


class KramdownError(Exception):
    '''Error class for kramdown-rfc errors'''
    pass


class MmarkError(Exception):
    '''Error class for mmark errors'''
    pass


class TextError(Exception):
    '''Error class for id2xml errors'''
    pass


def process_file(file, upload_dir, logger=getLogger()):
    '''Returns XML version of the given file.
    NOTE: if file is an XML file, that file wouldn't go through conversion.'''

    (dir_path, filename) = save_file(file, upload_dir)

    logger.info('file saved at {}'.format(filename))

    file_ext = get_extension(filename)

    if file_ext.lower() in ['.md', '.mkd']:
        filename = md2xml(filename, logger)
    elif file_ext.lower() == '.txt':
        filename = txt2xml(filename, logger)

    return (dir_path, filename)


def md2xml(filename, logger=getLogger()):
    '''Calls correct markdown processor for markdown files'''
    with open(filename, 'r') as file:
        first_line = file.readline().strip()

    if len(first_line) > 2 and first_line[:3] == '%%%':
        return mmark2xml(filename, logger)
    else:
        return kramdown2xml(filename, logger)


def kramdown2xml(filename, logger=getLogger()):
    '''Convert kramdown-rfc markdown file to XML'''

    logger.debug('processing kramdown-rfc file')

    output = proc_run(
                args=['kramdown-rfc', '--v3', filename],
                capture_output=True)

    try:
        output.check_returncode()
    except CalledProcessError:
        logger.info('kramdown-rfc error: {}'.format(
            output.stderr.decode('utf-8')))
        raise KramdownError(output.stderr.decode('utf-8'))

    # write output to XML file
    xml_file = get_filename(filename, 'xml')
    with open(xml_file, 'wb') as file:
        file.write(output.stdout)

    logger.info('new file saved at {}'.format(xml_file))
    return xml_file


def mmark2xml(filename, logger=getLogger()):
    '''Convert mmark markdown file to XML'''

    logger.debug('processing mmark file')

    output = proc_run(
                args=['mmark', filename],
                capture_output=True)

    try:
        output.check_returncode()
    except CalledProcessError:
        if output.stderr:
            error = output.stderr.decode('utf-8')
            logger.info('mmark error: {}'.format(error))
        else:
            error = 'mmark error'
            logger.info('mmark error: no stderr output')
        raise MmarkError(error)

    # write output to XML file
    xml_file = get_filename(filename, 'xml')
    with open(xml_file, 'wb') as file:
        file.write(output.stdout)

    logger.info('new file saved at {}'.format(xml_file))
    return xml_file


def txt2xml(filename, logger=getLogger()):
    '''Convert text RFC file to XML'''

    logger.debug('processing text RFC file')

    xml_file = get_filename(filename, 'xml')

    output = proc_run(
                args=['id2xml', '--v2', '--out', xml_file, filename],
                capture_output=True)

    try:
        output.check_returncode()
    except CalledProcessError:
        logger.info('id2xml error: {}'.format(
            output.stderr.decode('utf-8')))
        raise TextError(output.stderr.decode('utf-8'))

    logger.info('new file saved at {}'.format(xml_file))
    return xml_file


def convert_v2v3(filename, logger=getLogger()):
    '''Convert XML2RFC v2 file to v3'''
    logger.debug('converting v2 XML to v3 XML')

    xml_file = get_filename(filename, 'xml')

    output = proc_run(
                args=[
                    'xml2rfc', '--v2v3', '--out', xml_file,
                    filename],
                capture_output=True)

    try:
        output.check_returncode()
    except CalledProcessError:
        errors = get_errors(output, filename)
        if errors:
            logger.info('xml2rfc v2v3 error: {}'.format(errors))
        else:
            errors = 'v2v3 conversion error'
            logger.info('xml2rfc v2v3 error: no error output')
        raise XML2RFCError(errors)

    logs = process_xml2rfc_log(output, filename)

    logger.info('new file saved at {}'.format(xml_file))
    return (xml_file, logs)


def get_xml(filename, logger=getLogger()):
    '''Convert/parse XML to XML2RFC v3
    NOTE: if file is XML2RFC v2 that will get converted to v3'''

    logs = None

    try:
        logger.debug('invoking xml2rfc parser')

        parser = XmlRfcParser(filename)
        xmltree = parser.parse(remove_comments=False)
        xmlroot = xmltree.getroot()
        xml2rfc_version = xmlroot.get('version', '2')

        if xml2rfc_version == '2':
            filename, logs = convert_v2v3(filename, logger)
    except (XmlRfcError, XMLSyntaxError) as e:
        logger.info('xml2rfc error: {}'.format(str(e)))
        raise XML2RFCError(e)

    logger.info('new file saved at {}'.format(filename))
    return (filename, logs)


def get_html(filename, logger=getLogger()):
    '''Render HTML'''
    logger.debug('running xml2rfc html converter')

    html_file = get_filename(filename, 'html')

    output = proc_run(
                args=[
                    'xml2rfc', '--html', '--out', html_file,
                    filename],
                capture_output=True)

    try:
        output.check_returncode()
    except CalledProcessError:
        errors = get_errors(output, filename)
        if errors:
            logger.info('xml2rfc html error: {}'.format(errors))
        else:
            errors = 'html generation error'
            logger.info('xml2rfc html error: no error output')
        raise XML2RFCError(errors)

    logger.info('new file saved at {}'.format(html_file))
    return (html_file, process_xml2rfc_log(output, filename))


def get_text(filename, logger=getLogger()):

    text_file = get_filename(filename, 'txt')

    output = proc_run(
                args=[
                    'xml2rfc', '--text', '--out', text_file,
                    filename],
                capture_output=True)

    try:
        output.check_returncode()
    except CalledProcessError:
        errors = get_errors(output, filename)
        if errors:
            logger.info('xml2rfc text error: {}'.format(errors))
        else:
            errors = 'text generation error'
            logger.info('xml2rfc text error: no error output')
        raise XML2RFCError(errors)

    logger.info('new file saved at {}'.format(text_file))
    return (text_file, process_xml2rfc_log(output, filename))


def get_pdf(filename, logger=getLogger()):
    '''Render PDF'''
    logger.debug('running xml2rfc pdf converter')

    pdf_file = get_filename(filename, 'pdf')

    output = proc_run(
                args=[
                    'xml2rfc', '--pdf', '--out', pdf_file,
                    filename],
                capture_output=True)

    try:
        output.check_returncode()
    except CalledProcessError:
        errors = get_errors(output, filename)
        if errors:
            logger.info('xml2rfc pdf error: {}'.format(errors))
        else:
            errors = 'pdf generation error'
            logger.info('xml2rfc pdf error: no error output')
        raise XML2RFCError(errors)

    logger.info('new file saved at {}'.format(pdf_file))
    return (pdf_file, process_xml2rfc_log(output, filename))


def clean_svg_ids(filename, logger=getLogger()):
    '''Clean SVGs with duplicates IDs in XML'''
    logger.debug('invoking kramdown-rfc-clean-svg-ids')

    output = proc_run(
                args=['kramdown-rfc-clean-svg-ids', filename],
                capture_output=True)

    # write output to XML file
    xml_file = get_filename(filename, 'xml')
    with open(xml_file, 'wb') as file:
        file.write(output.stdout)

    logger.info('new file saved at {}'.format(xml_file))
    return xml_file
