from os import path

from flask import Blueprint, current_app, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename
from xml2rfc import HtmlWriter, PrepToolWriter, V2v3XmlWriter, XmlRfcParser

ALLOWED_EXTENSIONS = {'txt', 'xml', 'md'}

bp = Blueprint('api', __name__, url_prefix='/api')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_filename(filename, ext):
    root, _ = path.splitext(filename)
    return '.'.join([root, ext])


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

    # run prep tool
    prep = PrepToolWriter(xmltree, quiet=True, liberal=True)
    prep.options.accept_prepped = True
    xmltree.tree = prep.prep()

    # return html
    html = HtmlWriter(xmltree, quiet=True)
    html_file = get_filename(filename, 'html')
    html.write(html_file)
    return html_file.split('/')[-1]


@bp.route('/render', methods=('POST',))
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

        html_file = render_xml(filename)
        return send_from_directory(
                current_app.config['UPLOAD_DIR'],
                html_file,
                as_attachment=True)
