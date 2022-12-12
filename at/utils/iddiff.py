from logging import getLogger
from subprocess import run as proc_run, CalledProcessError


OK = 200
ALLOWED_SCHEMES = ['http', 'https']


# Exceptions
class IddiffError(Exception):
    '''Error class for iddiff errors'''
    pass


def get_id_diff(old_draft, new_draft, diff_tool='iddiff', table=False,
                wdiff=False, chbars=False, abdiff=False, logger=getLogger()):
    '''Returns iddiff output'''

    if diff_tool == 'rfcdiff':
        logger.debug('running rfcdiff')
        diff = ['rfcdiff', '--stdout', ]
    else:
        logger.debug('running iddiff')
        diff = ['iddiff', ]

    if wdiff:
        output = proc_run(args=diff + ['--hwdiff', old_draft, new_draft],
                          capture_output=True)
    elif chbars:
        output = proc_run(args=diff + ['--chbars', old_draft, new_draft],
                          capture_output=True)
    elif abdiff:
        output = proc_run(args=diff + ['--abdiff', old_draft, new_draft],
                          capture_output=True)
    elif table and diff_tool == 'iddiff':
        output = proc_run(args=diff + ['-t', old_draft, new_draft],
                          capture_output=True)
    else:
        output = proc_run(args=diff + [old_draft, new_draft],
                          capture_output=True)

    try:
        output.check_returncode()
    except CalledProcessError:
        logger.info('iddiff error: {}:'.format(output.stderr.decode('utf-8')))
        raise IddiffError(output.stderr.decode('utf-8'))

    return output.stdout.decode('utf-8')
