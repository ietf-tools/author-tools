from re import compile as re_compile, IGNORECASE

XML2RFC_ERROR_REGEX = re_compile(r'^.* Error: (?P<message>.*)$', IGNORECASE)
XML2RFC_WARN_REGEX = re_compile(r'^.* Warning: (?P<message>.*)$', IGNORECASE)


def process_xml2rfc_log(output):
    '''Process xml2rfc output and return dictionary of errors and warnings'''
    log = []
    errors = []
    warnings = []

    if output.stdout:
        log += output.stdout.decode('utf-8', errors='ignore').split('\n')
    if output.stderr:
        log += output.stderr.decode('utf-8', errors='ignore').split('\n')

    for line in log:
        error = XML2RFC_ERROR_REGEX.search(line)
        warning = XML2RFC_WARN_REGEX.search(line)
        if error and error.group('message'):
            errors.append(error.group('message'))
        elif warning and warning.group('message'):
            warnings.append(warning.group('message'))

    return {'errors': errors, 'warnings': warnings}


def get_errors(output):
    '''Returns errors as a string'''

    log = process_xml2rfc_log(output)

    if len(log['errors']) > 0:
        return '\n'.join(log['errors'])
    else:
        return None
