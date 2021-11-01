from logging import getLogger
from subprocess import run as proc_run, CalledProcessError


# Exceptions
class IddiffError(Exception):
    '''Error class for iddiff errors'''
    pass


def get_id_diff(filename_1, filename_2, logger=getLogger()):
    '''Returns iddiff output'''

    logger.debug('running iddiff')

    output = proc_run(
                args=['iddiff', filename_1, filename_2], capture_output=True)

    try:
        output.check_returncode()
    except CalledProcessError:
        logger.info('iddiff error: {}:'.format(output.stderr.decode('utf-8')))
        raise IddiffError(output.stderr.decode('utf-8'))

    return output.stdout.decode('utf-8')
