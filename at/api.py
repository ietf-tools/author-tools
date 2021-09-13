from logging import getLogger
from os import mkdir, path
from subprocess import run as proc_run, CalledProcessError
from uuid import uuid4

from flask import (
        Blueprint, current_app, jsonify, request, send_from_directory)
from lxml.etree import XMLSyntaxError
from werkzeug.utils import secure_filename
from xml2rfc.writers.base import default_options
from xml2rfc import (
        HtmlWriter, PdfWriter, PrepToolWriter, TextWriter, V2v3XmlWriter,
        __version__ as xml2rfc_version, XmlRfcParser)
from xml2rfc.writers.base import RfcWriterError

ALLOWED_EXTENSIONS = ('txt', 'xml', 'md', 'mkd')
DIR_MODE = 0o770
BAD_REQUEST = 400
UNAUTHORIZED = 401
METADATA_JS_URL = 'https://www.rfc-editor.org/js/metadata.min.js'

bp = Blueprint('api', __name__, url_prefix='/api')


# Exceptions
class KramdownError(Exception):
    '''Error class for kramdown-rfc2629 errors'''
    pass


class TextError(Exception):
    '''Error class for id2xml errors'''
    pass


class XML2RFCError(Exception):
    '''Error class for xml2rfc errors'''
    pass


def allowed_file(filename):
    '''Return true if file extension in allowed list'''

    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_filename(filename, ext):
    '''Returns filename with given extension'''

    root, _ = path.splitext(filename)
    return '.'.join([root, ext])


def get_file(filename):
    '''Returns the filename part from a file path'''

    return filename.split('/')[-1]


def process_file(file, upload_dir, logger=getLogger()):
    '''Returns XML version of the given file.
    NOTE: if file is an XML file, that file wouldn't go through conversion.'''

    dir_path = path.join(upload_dir, str(uuid4()))
    mkdir(dir_path, mode=DIR_MODE)

    filename = path.join(
            dir_path,
            secure_filename(file.filename))
    file.save(filename)

    logger.info('file saved at {}'.format(filename))

    _, file_ext = path.splitext(filename)

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
    except CalledProcessError as e:
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
    except CalledProcessError as e:
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
    options.metadata_js_url = METADATA_JS_URL

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


def get_kramdown_rfc2629_version(logger=getLogger()):
    '''Return kramdown-rfc2629 version'''

    output = proc_run(
                args=['kramdown-rfc2629', '--version'],
                capture_output=True)

    try:
        output.check_returncode()
        return output.stdout.decode('utf-8').replace(
                'kramdown-rfc2629', '').strip()
    except CalledProcessError as e:
        logger.info('kramdown-rfc2629 error: {}'.format(
            output.stderr.decode('utf-8')))
        return None


def get_id2xml_version(logger=getLogger()):
    '''Return id2xml version'''

    output = proc_run(args=['id2xml', '--version'], capture_output=True)

    try:
        output.check_returncode()
        return output.stdout.decode('utf-8').replace('id2xml', '').strip()
    except CalledProcessError as e:
        logger.info('id2xml error: {}'.format(
            output.stderr.decode('utf-8')))
        return None


@bp.route('/render/<format>', methods=('POST',))
def render(format):
    '''POST: /render/<format> API call
    Returns rendered format of the given input file.
    Returns JSON on event of an error.'''

    logger = current_app.logger

    # NOTE: this authentication is only fit for the PoC testing phase
    # and needs to be replaced.
    if 'API_KEYS' in current_app.config.keys():
        if 'apikey' in request.values.keys():
            if request.values['apikey'] in current_app.config['API_KEYS']:
                logger.debug('valid apikey')
            else:
                logger.error('invalid api key')
                return jsonify(error='API key is invalid'), UNAUTHORIZED
        else:
            logger.error('missing api key')
            return jsonify(error='API key is missing'), UNAUTHORIZED

    if 'file' not in request.files:
        logger.info('no input file')
        return jsonify(error='No file'), BAD_REQUEST

    file = request.files['file']

    if file.filename == '':
        logger.info('file name missing')
        return jsonify(error='Filename is missing'), BAD_REQUEST

    if file and allowed_file(file.filename):
        try:
            dir_path, filename = process_file(
                    file=file,
                    upload_dir=current_app.config['UPLOAD_DIR'],
                    logger=logger)
        except KramdownError as e:
            return jsonify(
                    error='kramdown-rfc2629 error: {}'.format(e)), BAD_REQUEST
        except TextError as e:
            return jsonify(error='id2xml error: {}'.format(e)), BAD_REQUEST

        try:
            xml_file = get_xml(filename, logger=logger)
        except XML2RFCError as e:
            return jsonify(error='xml2rfc error: {}'.format(e)), BAD_REQUEST

        rendered_filename = ''

        try:
            if format == 'xml':
                rendered_filename = get_file(xml_file)
            elif format == 'html':
                html_file = get_html(xml_file, logger=logger)
                rendered_filename = get_file(html_file)
            elif format == 'text':
                text_file = get_text(xml_file, logger=logger)
                rendered_filename = get_file(text_file)
            elif format == 'pdf':
                pdf_file = get_pdf(xml_file, logger=logger)
                rendered_filename = get_file(pdf_file)
            else:
                logger.info(
                        'render format not supported: {}'.format(format))
                return jsonify(
                        error='Render format not supported'), BAD_REQUEST
        except XML2RFCError as e:
            return jsonify(error='xml2rfc error: {}'.format(e)), BAD_REQUEST

        return send_from_directory(
                dir_path,
                get_file(rendered_filename),
                as_attachment=True)
    else:
        logger.info('File format not supportted: {}'.format(file.filename))
        return jsonify(error='Input file format not supported'), BAD_REQUEST


@bp.route('/version', methods=('GET',))
def version():
    '''GET: /version API call
    Returns JSON with version information'''

    logger = current_app.logger
    logger.debug('version information request')

    version_information = {
            'author_tools_api': current_app.config['VERSION'],
            'xml2rfc': xml2rfc_version,
            'kramdown-rfc2629': get_kramdown_rfc2629_version(logger),
            'id2xml': get_id2xml_version(logger)}

    return jsonify(versions=version_information)
