from logging import getLogger
from subprocess import run as proc_run


def extract_abnf(filename, logger=getLogger()):
    '''Extract ABNF using BAP aex'''
    logger.debug('running bap aex')

    output = proc_run(args=['aex', filename], capture_output=True)
    result = ''

    if output.stderr:
        error = output.stderr.decode('utf-8')
        result += error
        logger.info('bap aex error: {}'.format(error))

    if output.stdout:
        result += output.stdout.decode('utf-8', errors='ignore')

    if result == '':
        result = 'No output from BAP aex.'

    return result
