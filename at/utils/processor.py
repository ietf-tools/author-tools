from logging import getLogger
from subprocess import run as proc_run, CalledProcessError

from xml2rfc.writers.base import default_options
from xml2rfc import (
        HtmlWriter, PdfWriter, PrepToolWriter, TextWriter, V2v3XmlWriter,
        XmlRfcParser)
from xml2rfc.writers.base import RfcWriterError
from lxml.etree import XMLSyntaxError

from at.utils.file import get_extension, get_filename, save_file


# Exceptions
class XML2RFCError(Exception):
    '''Error class for xml2rfc errors'''
    pass


class KramdownError(Exception):
    '''Error class for kramdown-rfc2629 errors'''
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
    '''Convert kramdown-rfc2629 markdown file to XML'''

    logger.debug('processing kramdown-rfc2629 file')

    output = proc_run(
                args=['kramdown-rfc2629', filename],
                capture_output=True)

    try:
        output.check_returncode()
    except CalledProcessError:
        logger.info('kramdown-rfc2629 error: {}'.format(
            output.stderr.decode('utf-8')))
        raise KramdownError(output.stderr.decode('utf-8'))

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
                args=['id2xml', '--v3', '--out', xml_file, filename],
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
    try:
        logger.debug('converting v2 XML to v3 XML')

        # Update default options
        options = default_options
        options.v2v3 = True
        options.utf8 = True
        options.vocabulary = 'v2'
        options.no_dtd = True

        parser = XmlRfcParser(filename, options=options, quiet=True)
        xmltree = parser.parse(
                remove_comments=False,
                quiet=True,
                normalize=False,
                strip_cdata=False,
                add_xmlns=True)

        xml_file = get_filename(filename, 'v2v3.xml')
        options.output_filename = xml_file

        v2v3 = V2v3XmlWriter(xmltree, options=options, quiet=True)
        v2v3.write(xml_file)
    except XMLSyntaxError as e:
        logger.info('xml2rfc v2v3 error: {}'.format(str(e)))
        raise XML2RFCError(e)

    logger.info('new file saved at {}'.format(xml_file))
    return xml_file


def get_xml(filename, logger=getLogger()):
    '''Convert/parse XML to XML2RFC v3
    NOTE: if file is XML2RFC v2 that will get converted to v3'''

    try:
        logger.debug('invoking xml2rfc parser')

        parser = XmlRfcParser(filename, quiet=True)
        xmltree = parser.parse(remove_comments=False, quiet=True)
        xmlroot = xmltree.getroot()
        xml2rfc_version = xmlroot.get('version', '2')

        if xml2rfc_version == '2':
            filename = convert_v2v3(filename, logger)

    except XMLSyntaxError as e:
        logger.info('xml2rfc error: {}'.format(str(e)))
        raise XML2RFCError(e)

    logger.info('new file saved at {}'.format(filename))
    return filename


def prep_xml(filename, logger=getLogger()):
    '''Prepare XML file with xml2rfc'''

    try:
        parser = XmlRfcParser(filename, quiet=True)
        xmltree = parser.parse(remove_comments=False, quiet=True)

        # run prep tool
        logger.debug('running xml2rfc prep tool')
        prep = PrepToolWriter(xmltree, quiet=True, liberal=True)
        prep.options.accept_prepped = True
        xmltree.tree = prep.prep()
    except RfcWriterError as e:
        logger.error('xml2rfc preptool error: {}'.format(str(e)))
        raise XML2RFCError(e)

    if xmltree.tree is None:
        raise XML2RFCError(prep.errors)

    return xmltree


def get_html(filename, logger=getLogger()):
    '''Render HTML'''

    xmltree = prep_xml(filename)

    # Update default options
    options = default_options

    # render html
    logger.debug('running xml2rfc html writer')
    html = HtmlWriter(xmltree, options=options, quiet=True)
    html_file = get_filename(filename, 'html')
    html.write(html_file)

    logger.info('new file saved at {}'.format(html_file))
    return html_file


def get_text(filename, logger=getLogger()):
    '''Render text'''

    xmltree = prep_xml(filename)

    # render text
    logger.debug('running xml2rfc text writer')
    text = TextWriter(xmltree, quiet=True)
    text_file = get_filename(filename, 'txt')
    text.write(text_file)

    logger.info('new file saved at {}'.format(text_file))
    return text_file


def get_pdf(filename, logger=getLogger()):
    '''Render PDF'''

    xmltree = prep_xml(filename)

    # render pdf
    logger.debug('running xml2rfc pdf writer')
    pdf = PdfWriter(xmltree, quiet=True)
    pdf_file = get_filename(filename, 'pdf')
    pdf.write(pdf_file)

    logger.info('new file saved at {}'.format(pdf_file))
    return pdf_file
