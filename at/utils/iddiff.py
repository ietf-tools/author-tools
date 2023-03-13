from logging import getLogger
from subprocess import run as proc_run, CalledProcessError, TimeoutExpired


OK = 200
ALLOWED_SCHEMES = ['http', 'https']
TIMEOUT = 20  # in seconds


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

    try:
        if wdiff:
            output = proc_run(args=diff + ['--hwdiff', old_draft, new_draft],
                              timeout=TIMEOUT,
                              capture_output=True)
        elif chbars:
            output = proc_run(args=diff + ['--chbars', old_draft, new_draft],
                              timeout=TIMEOUT,
                              capture_output=True)
        elif abdiff:
            output = proc_run(args=diff + ['--abdiff', old_draft, new_draft],
                              timeout=TIMEOUT,
                              capture_output=True)
        elif table and diff_tool == 'iddiff':
            output = proc_run(args=diff + ['-t', old_draft, new_draft],
                              timeout=TIMEOUT,
                              capture_output=True)
        else:
            output = proc_run(args=diff + [old_draft, new_draft],
                              timeout=TIMEOUT,
                              capture_output=True)
    except TimeoutExpired:
        if diff_tool == 'rfcdiff':
            logger.info('iddiff error: Timeout error.')
            raise IddiffError('Timeout while running comparison.')
        else:
            # try again with rfcdiff
            return get_id_diff(old_draft, new_draft, diff_tool='rfcdiff',
                               table=table, wdiff=wdiff, chbars=chbars,
                               abdiff=abdiff, logger=logger)

    try:
        output.check_returncode()
    except CalledProcessError:
        logger.info('iddiff error: {}'.format(output.stderr.decode('utf-8')))
        raise IddiffError(output.stderr.decode('utf-8'))

    return output.stdout.decode('utf-8')
