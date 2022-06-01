from logging import getLogger
from os.path import dirname
from subprocess import run as proc_run, CalledProcessError

from xml2rfc import XmlRfcParser
from lxml.etree import XMLSyntaxError

from at.utils.file import get_filename
from at.utils.logs import process_xml2rfc_log
from at.utils.processor import XML2RFCError


def validate_xml(filename, logger=getLogger()):
    '''Validate XML2RFC
    NOTE: if file is XML2RFC v2 that will get converted to v3'''

    try:
        log = None

        logger.debug('invoking xml2rfc parser')

        parser = XmlRfcParser(filename, quiet=True)
        xmltree = parser.parse(remove_comments=False, quiet=True)
        xmlroot = xmltree.getroot()
        xml2rfc_version = xmlroot.get('version', '2')
        v2_processed_log = None

        if xml2rfc_version == '2':
            filename, output = convert_v2v3(filename, logger)
            v2_processed_log = process_xml2rfc_log(output)

    except XMLSyntaxError as e:
        logger.info('xml2rfc error: {}'.format(str(e)))
        raise XML2RFCError(e)

    logger.info('new file saved at {}'.format(filename))

    log, text_file = xml2rfc_validation(filename, logger)
    processed_log = process_xml2rfc_log(log)

    idnits_log = idnits(text_file, logger)

    if v2_processed_log:
        processed_log = {
                k: v2_processed_log[k] + v for k, v in processed_log.items()}

    processed_log['idnits'] = idnits_log

    return processed_log


def xml2rfc_validation(filename, logger=getLogger()):
    '''Run xml2rfc to validate the document and return output and text file'''

    logger.debug('running xml2rfc')

    text_file = get_filename(filename, 'txt')

    output = proc_run(
                args=['xml2rfc', '--out', text_file,  filename],
                capture_output=True)

    try:
        output.check_returncode()
    except CalledProcessError:
        if output.stderr:
            logger.info('xml2rfc error: {}'.format(output.stderr))
        else:
            logger.info('xml2rfc error: no stderr output')

    return (output, text_file)


def convert_v2v3(filename, logger=getLogger()):
    '''Convert XML2RFC v2 file to v3 and return file name output'''

    logger.debug('converting v2 XML to v3 XML')

    xml_file = get_filename(filename, 'xml')

    output = proc_run(
                args=['xml2rfc', '--v2v3', '--out', xml_file, filename],
                capture_output=True)

    try:
        output.check_returncode()
    except CalledProcessError:
        if output.stderr:
            error = output.stderr.decode('utf-8')
            logger.info('xml2rfc v2v3 error: {}'.format(error))
        else:
            error = 'v2v3 conversion error'
            logger.info('xml2rfc v2v3 error: no stderr output')
        raise XML2RFCError(error)

    logger.info('new file saved at {}'.format(xml_file))
    return xml_file, output


def idnits(filename,
           logger=getLogger(),
           verbose='0',
           show_text=False,
           year=False,
           submit_check=False):
    '''Running idnits and return output'''

    logger.debug('running idnits')

    args = ['idnits']
    if verbose == '1':
        args.append('--verbose')
    elif verbose == '2':
        args.append('--verbose')
        args.append('--verbose')    # add --verbose twice
    if show_text:
        args.append('--showtext')
    if year:
        args.append('--year')
        args.append(str(year))
    if submit_check:
        args.append('--submitcheck')
    args.append(filename)

    output = proc_run(
                args=args,
                capture_output=True)
    error = None

    try:
        output.check_returncode()
    except CalledProcessError:
        if output.stderr:
            error = output.stderr.decode('utf-8')
            logger.info('idnits error: {}'.format(error))
        else:
            error = 'Error occured while running idnits'
            logger.info('idnits error: no stderr output')

    if output.stdout:
        stdout = output.stdout.decode('utf-8', errors='ignore')
        return stdout.replace(dirname(filename), '')
    else:
        return error
