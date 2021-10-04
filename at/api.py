from flask import (
        Blueprint, current_app, jsonify, request, send_from_directory)

from at.utils.authentication import require_api_key
from at.utils.file import allowed_file, get_file
from at.utils.processor import (
        get_html, get_pdf, get_text, get_xml, process_file, KramdownError,
        MmarkError, TextError, XML2RFCError)
from at.utils.version import (
        get_id2xml_version, get_goat_version, get_mmark_version,
        get_kramdown_rfc2629_version, get_weasyprint_version,
        get_xml2rfc_version)

BAD_REQUEST = 400
UNAUTHORIZED = 401

bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/render/<format>', methods=('POST',))
@require_api_key
def render(format):
    '''POST: /render/<format> API call
    Returns rendered format of the given input file.
    Returns JSON on event of an error.'''

    logger = current_app.logger

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
        except MmarkError as e:
            return jsonify(
                    error='mmark error: {}'.format(e)), BAD_REQUEST
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
            'xml2rfc': get_xml2rfc_version(),
            'kramdown-rfc2629': get_kramdown_rfc2629_version(logger),
            'mmark': get_mmark_version(logger),
            'id2xml': get_id2xml_version(logger),
            'weasyprint': get_weasyprint_version(),
            'goat': get_goat_version(logger)}

    return jsonify(versions=version_information)
