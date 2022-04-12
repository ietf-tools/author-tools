from flask import (
        Blueprint, current_app, jsonify, request, send_from_directory)

from at.utils.authentication import require_api_key
from at.utils.file import (
        allowed_file, get_file, get_name, get_name_with_revision,
        DownloadError)
from at.utils.iddiff import (
        get_id_diff, get_latest, get_text_id_from_file, get_text_id_from_url,
        is_valid_url, IddiffError, InvalidURL, LatestDraftNotFound)
from at.utils.processor import (
        get_html, get_pdf, get_text, get_xml, process_file, KramdownError,
        MmarkError, TextError, XML2RFCError)
from at.utils.validation import validate_xml
from at.utils.version import (
        get_aasvg_version, get_idnits_version, get_id2xml_version,
        get_iddiff_version, get_mmark_version, get_kramdown_rfc_version,
        get_weasyprint_version, get_xml2rfc_version)

BAD_REQUEST = 400

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
        logger.info('filename missing')
        return jsonify(error='Filename is missing'), BAD_REQUEST

    if file and allowed_file(file.filename):
        try:
            dir_path, filename = process_file(
                    file=file,
                    upload_dir=current_app.config['UPLOAD_DIR'],
                    logger=logger)
        except KramdownError as e:
            return jsonify(
                    error='kramdown-rfc error: {}'.format(e)), BAD_REQUEST
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


@bp.route('/validate', methods=('POST',))
@require_api_key
def validate():
    '''POST: /validate API call
    Returns JSON with errors, warnings and informational output'''

    logger = current_app.logger

    if 'file' not in request.files:
        logger.info('no input file')
        return jsonify(error='No file'), BAD_REQUEST

    file = request.files['file']

    if file.filename == '':
        logger.info('filename missing')
        return jsonify(error='Filename is missing'), BAD_REQUEST

    if file and allowed_file(file.filename):
        try:
            _, filename = process_file(
                    file=file,
                    upload_dir=current_app.config['UPLOAD_DIR'],
                    logger=logger)
        except KramdownError as e:
            return jsonify(
                    error='kramdown-rfc error: {}'.format(e)), BAD_REQUEST
        except MmarkError as e:
            return jsonify(
                    error='mmark error: {}'.format(e)), BAD_REQUEST
        except TextError as e:
            return jsonify(error='id2xml error: {}'.format(e)), BAD_REQUEST

        try:
            log = validate_xml(filename, logger=logger)
        except XML2RFCError as e:
            return jsonify(error='xml2rfc error: {}'.format(e)), BAD_REQUEST

        return jsonify(log)
    else:
        logger.info('File format not supportted: {}'.format(file.filename))
        return jsonify(error='Input file format not supported'), BAD_REQUEST


@bp.route('/iddiff', methods=('POST', 'GET'))
@require_api_key
def id_diff():
    '''POST: /iddiff API call
    Returns HTML output of ID diff
    Returns JSON on event of an error.'''

    logger = current_app.logger

    doc_1 = request.values.get('doc_1', '').strip()
    doc_2 = request.values.get('doc_2', '').strip()
    url_1 = request.values.get('url_1', '').strip()
    url_2 = request.values.get('url_2', '').strip()

    # allow single parameters for doc_? and url_?
    if 'file_1' not in request.files and not doc_1 and not url_1:
        if doc_2:
            doc_1 = doc_2
            doc_2 = ''
        elif url_2:
            url_1 = url_2
            url_2 = ''

    single_draft = False

    if request.values.get('table', False):
        table = True
    else:
        table = False

    if not doc_1 and not url_1:
        if 'file_1' not in request.files:
            logger.info('no documents to compare')
            return jsonify(error='No documents to compare'), BAD_REQUEST
        else:
            file_1 = request.files['file_1']

        if file_1.filename == '':
            logger.info('first draft filename missing')
            return jsonify(
                    error='Filename of first draft missing'), BAD_REQUEST

        if file_1 and allowed_file(file_1.filename):
            try:
                dir_path_1, filename_1 = get_text_id_from_file(
                        file=file_1,
                        upload_dir=current_app.config['UPLOAD_DIR'])
            except IddiffError as e:
                error = 'Error converting first draft to text: {}' \
                        .format(str(e))
                return jsonify(error=error), BAD_REQUEST
        else:
            logger.info('File format not supportted: {}'.format(
                                                            file_1.filename))
            return jsonify(
                        error='First file format not supported'), BAD_REQUEST
    elif doc_1:
        try:
            url = get_latest(doc_1,
                             current_app.config['DT_LATEST_DRAFT_URL'],
                             logger)
        except LatestDraftNotFound as e:
            return jsonify(error=str(e)), BAD_REQUEST
        except DownloadError as e:
            return jsonify(error=str(e)), BAD_REQUEST

        try:
            dir_path_1, filename_1 = get_text_id_from_url(
                                            url,
                                            current_app.config['UPLOAD_DIR'],
                                            logger)
        except DownloadError as e:
            return jsonify(error=str(e)), BAD_REQUEST
    else:
        try:
            if is_valid_url(url_1,
                            current_app.config['IDDIFF_ALLOWED_DOMAINS'],
                            logger):
                dir_path_1, filename_1 = get_text_id_from_url(
                                            url_1,
                                            current_app.config['UPLOAD_DIR'],
                                            logger)
        except InvalidURL as e:
            return jsonify(error=str(e)), BAD_REQUEST
        except DownloadError as e:
            return jsonify(error=str(e)), BAD_REQUEST

    if not doc_2 and not url_2:
        if 'file_2' not in request.files:
            filename = filename_1.split('/')[-1]
            draft_name = get_name(filename)
            original_draft = get_name_with_revision(filename)

            if draft_name is None:
                logger.error('Can not determine draft name for {}'.format(
                                                            file_1.filename))
                return jsonify(error='Can not determine draft/rfc')
            else:
                try:
                    url = get_latest(
                                    draft_name,
                                    current_app.config['DT_LATEST_DRAFT_URL'],
                                    original_draft,
                                    logger)
                    dir_path_2, filename_2 = get_text_id_from_url(
                                            url,
                                            current_app.config['UPLOAD_DIR'],
                                            logger)
                    single_draft = True
                except LatestDraftNotFound as e:
                    return jsonify(error=str(e)), BAD_REQUEST
                except DownloadError as e:
                    return jsonify(error=str(e)), BAD_REQUEST
        else:
            file_2 = request.files['file_2']

            if file_2.filename == '':
                logger.info('second draft filename missing')
                return jsonify(
                        error='Filename of second draft missing'), BAD_REQUEST

            if file_2 and allowed_file(file_2.filename):
                try:
                    dir_path_2, filename_2 = get_text_id_from_file(
                            file=file_2,
                            upload_dir=current_app.config['UPLOAD_DIR'])
                except IddiffError as e:
                    error = 'Error converting second draft to text: {}' \
                            .format(str(e))
                    return jsonify(error=error), BAD_REQUEST
            else:
                logger.info('File format not supportted: {}'.format(
                                                            file_2.filename))
                return jsonify(
                        error='Second file format not supported'), BAD_REQUEST
    elif doc_2:
        try:
            url = get_latest(doc_2,
                             current_app.config['DT_LATEST_DRAFT_URL'],
                             logger)
        except LatestDraftNotFound as e:
            return jsonify(error=str(e)), BAD_REQUEST

        try:
            dir_path_2, filename_2 = get_text_id_from_url(
                                            url,
                                            current_app.config['UPLOAD_DIR'],
                                            logger)
        except DownloadError as e:
            return jsonify(error=str(e)), BAD_REQUEST
    else:
        try:
            if is_valid_url(url_2,
                            current_app.config['IDDIFF_ALLOWED_DOMAINS'],
                            logger):
                dir_path_2, filename_2 = get_text_id_from_url(
                                            url_2,
                                            current_app.config['UPLOAD_DIR'],
                                            logger)
        except InvalidURL as e:
            return jsonify(error=str(e)), BAD_REQUEST
        except DownloadError as e:
            return jsonify(error=str(e)), BAD_REQUEST

    try:
        if single_draft:
            old_draft = filename_2
            new_draft = filename_1
        else:
            old_draft = filename_1
            new_draft = filename_2
        iddiff = get_id_diff(old_draft=old_draft,
                             new_draft=new_draft,
                             table=table,
                             logger=logger)
        for dir_path in (dir_path_1, dir_path_2):
            iddiff = iddiff.replace('{}/'.format(dir_path), '')
        return iddiff
    except IddiffError as e:
        return jsonify(error='iddiff error: {}'.format(e)), BAD_REQUEST


@bp.route('/version', methods=('GET',))
def version():
    '''GET: /version API call
    Returns JSON with version information'''

    logger = current_app.logger
    logger.debug('version information request')

    version_information = {
            'author_tools_api': current_app.config['VERSION'],
            'xml2rfc': get_xml2rfc_version(),
            'kramdown-rfc': get_kramdown_rfc_version(logger),
            'mmark': get_mmark_version(logger),
            'id2xml': get_id2xml_version(logger),
            'weasyprint': get_weasyprint_version(),
            'idnits': get_idnits_version(logger),
            'iddiff': get_iddiff_version(logger),
            'aasvg': get_aasvg_version(logger)}

    return jsonify(versions=version_information)
