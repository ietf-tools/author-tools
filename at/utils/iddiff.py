from logging import getLogger
from subprocess import run as proc_run, CalledProcessError


OK = 200
ALLOWED_SCHEMES = ['http', 'https']


# Exceptions
class IddiffError(Exception):
    '''Error class for iddiff errors'''
    pass


def get_id_diff(old_draft, new_draft, table=False, wdiff=False, chbars=False,
                logger=getLogger()):
    '''Returns iddiff output'''

    logger.debug('running iddiff')

    if wdiff:
        output = proc_run(args=['iddiff', '--hwdiff', old_draft, new_draft],
                          capture_output=True)
    elif chbars:
        output = proc_run(args=['iddiff', '--chbars', old_draft, new_draft],
                          capture_output=True)
    elif table:
        output = proc_run(args=['iddiff', '-t', old_draft, new_draft],
                          capture_output=True)
    else:
        output = proc_run(args=['iddiff', old_draft, new_draft],
                          capture_output=True)

    try:
        output.check_returncode()
    except CalledProcessError:
        logger.info('iddiff error: {}:'.format(output.stderr.decode('utf-8')))
        raise IddiffError(output.stderr.decode('utf-8'))

    return output.stdout.decode('utf-8')
