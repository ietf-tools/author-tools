from os import path
from subprocess import run as proc_run, CalledProcessError

from flask import Blueprint, current_app, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename
from xml2rfc import HtmlWriter, PrepToolWriter, V2v3XmlWriter, XmlRfcParser

ALLOWED_EXTENSIONS = {'txt', 'xml', 'md', 'mkd'}

bp = Blueprint('api', __name__, url_prefix='/api')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_filename(filename, ext):
    root, _ = path.splitext(filename)
    return '.'.join([root, ext])


def md2xml(filename):
    output = proc_run(
                args=['kramdown-rfc2629', filename],
                capture_output=True)

    output.check_returncode()   # raise CalledProcessError on non-zero

    # write output to XML file
    xml_file = get_filename(filename, 'xml')
    with open(xml_file, 'wb') as file:
        file.write(output.stdout)

    return xml_file


def render_xml(filename):
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

    return filename


def render_html(filename):
    parser = XmlRfcParser(filename, quiet=True)
    xmltree = parser.parse(remove_comments=False, quiet=True)

    # run prep tool
    prep = PrepToolWriter(xmltree, quiet=True, liberal=True)
    prep.options.accept_prepped = True
    xmltree.tree = prep.prep()

    # return html
    html = HtmlWriter(xmltree, quiet=True)
    html_file = get_filename(filename, 'html')
    html.write(html_file)
    return html_file.split('/')[-1]


@bp.route('/render/html', methods=('POST',))
def render():
    if 'file' not in request.files:
        return jsonify(error='No file')

    file = request.files['file']

    if file.filename == '':
        return jsonify(error='Filename missing')

    if file and allowed_file(file.filename):
        filename = path.join(
                current_app.config['UPLOAD_DIR'],
                secure_filename(file.filename))
        file.save(filename)

        _, file_ext = path.splitext(filename)

        if file_ext.lower() in ['.md', '.mkd']:
            try:
                filename = md2xml(filename)
            except CalledProcessError as e:
                return jsonify(error='kramdown-rfc2629 error')

        xml_file = render_xml(filename)
        html_file = render_html(xml_file)
        return send_from_directory(
                current_app.config['UPLOAD_DIR'],
                html_file,
                as_attachment=True)
