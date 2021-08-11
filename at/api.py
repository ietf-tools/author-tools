from os import mkdir, path
from subprocess import run as proc_run, CalledProcessError
from uuid import uuid4

from flask import Blueprint, current_app, jsonify, request, send_from_directory
from lxml.etree import XMLSyntaxError
from werkzeug.utils import secure_filename
from xml2rfc import (
        HtmlWriter, PdfWriter, PrepToolWriter, TextWriter, V2v3XmlWriter,
        XmlRfcParser)
from xml2rfc.writers.base import RfcWriterError

ALLOWED_EXTENSIONS = {'txt', 'xml', 'md', 'mkd'}
DIR_MODE = 0o770
BAD_REQUEST = 400

bp = Blueprint('api', __name__, url_prefix='/api')


# Exceptions
class KramdownError(Exception):
    pass


class TextError(Exception):
    pass


class XML2RFCError(Exception):
    pass


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_filename(filename, ext):
    root, _ = path.splitext(filename)
    return '.'.join([root, ext])


def get_file(filename):
    return filename.split('/')[-1]


def process_file(file):
    dir_path = path.join(
            current_app.config['UPLOAD_DIR'],
            str(uuid4()))
    mkdir(dir_path, mode=DIR_MODE)

    filename = path.join(
            dir_path,
            secure_filename(file.filename))
    file.save(filename)

    _, file_ext = path.splitext(filename)

    if file_ext.lower() in ['.md', '.mkd']:
        filename = md2xml(filename)
    elif file_ext.lower() == '.txt':
        filename = txt2xml(filename)

    return (dir_path, filename)


def md2xml(filename):
    output = proc_run(
                args=['kramdown-rfc2629', filename],
                capture_output=True)

    try:
        output.check_returncode()
    except CalledProcessError as e:
        raise KramdownError(output.stderr.decode('utf-8'))

    # write output to XML file
    xml_file = get_filename(filename, 'xml')
    with open(xml_file, 'wb') as file:
        file.write(output.stdout)

    return xml_file


def txt2xml(filename):
    xml_file = get_filename(filename, 'xml')

    output = proc_run(
                args=['id2xml', '--v3', '--out', xml_file, filename],
                capture_output=True)

    try:
        output.check_returncode()
    except CalledProcessError as e:
        raise TextError(output.stderr.decode('utf-8'))

    return xml_file


def get_xml(filename):
    try:
        parser = XmlRfcParser(filename, quiet=True)
        xmltree = parser.parse(remove_comments=False, quiet=True)
        xmlroot = xmltree.getroot()
        xml2rfc_version = xmlroot.get('version', '2')

        # v2v3 conversion for v2 XML
        if xml2rfc_version == '2':
            v2v3 = V2v3XmlWriter(xmltree)
            xmltree.tree = v2v3.convert2to3()
            xmlroot = xmltree.getroot()
            v2v3.write(filename)
    except XMLSyntaxError as e:
        raise XML2RFCError(e)

    return filename


def prep_xml(filename):
    try:
        parser = XmlRfcParser(filename, quiet=True)
        xmltree = parser.parse(remove_comments=False, quiet=True)

        # run prep tool
        prep = PrepToolWriter(xmltree, quiet=True, liberal=True)
        prep.options.accept_prepped = True
        xmltree.tree = prep.prep()
    except RfcWriterError as e:
        raise XML2RFCError(e)

    if xmltree.tree is None:
        raise XML2RFCError(prep.errors)

    return xmltree


def get_html(filename):
    xmltree = prep_xml(filename)

    # render html
    html = HtmlWriter(xmltree, quiet=True)
    html_file = get_filename(filename, 'html')
    html.write(html_file)

    return html_file


def get_text(filename):
    xmltree = prep_xml(filename)

    # render text
    text = TextWriter(xmltree, quiet=True)
    text_file = get_filename(filename, 'txt')
    text.write(text_file)

    return text_file


def get_pdf(filename):
    xmltree = prep_xml(filename)

    # render pdf
    pdf = PdfWriter(xmltree, quiet=True)
    pdf_file = get_filename(filename, 'pdf')
    pdf.write(pdf_file)

    return pdf_file


@bp.route('/render/<format>', methods=('POST',))
def render(format):
    if 'file' not in request.files:
        return jsonify(error='No file'), BAD_REQUEST

    file = request.files['file']

    if file.filename == '':
        return jsonify(error='Filename missing'), BAD_REQUEST

    if file and allowed_file(file.filename):
        try:
            dir_path, filename = process_file(file)
        except KramdownError as e:
            return jsonify(
                    error='kramdown-rfc2629 error: {}'.format(e)), BAD_REQUEST
        except TextError as e:
            return jsonify(error='id2xml error: {}'.format(e)), BAD_REQUEST

        try:
            xml_file = get_xml(filename)
        except XML2RFCError as e:
            return jsonify(error='xml2rfc error: {}'.format(e)), BAD_REQUEST

        rendered_filename = ''

        try:
            if format == 'xml':
                rendered_filename = get_file(xml_file)
            elif format == 'html':
                html_file = get_html(xml_file)
                rendered_filename = get_file(html_file)
            elif format == 'text':
                text_file = get_text(xml_file)
                rendered_filename = get_file(text_file)
            elif format == 'pdf':
                pdf_file = get_pdf(xml_file)
                rendered_filename = get_file(pdf_file)
            else:
                return jsonify(
                        error='render format not supported'), BAD_REQUEST
        except XML2RFCError as e:
            return jsonify(error='xml2rfc error: {}'.format(e)), BAD_REQUEST

        return send_from_directory(
                dir_path,
                get_file(rendered_filename),
                as_attachment=True)
