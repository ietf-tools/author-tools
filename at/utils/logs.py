from re import compile as re_compile, IGNORECASE

from at.utils.file import cleanup_output

XML2RFC_ERROR_REGEX = re_compile(r'^.*?Error: (?P<message>.*)$', IGNORECASE)
XML2RFC_WARN_REGEX = re_compile(r'^.*?Warning: (?P<message>.*)$', IGNORECASE)
XML2RFC_LINE_NUMBER_REGEX = re_compile(
                                r'^.*?\((?P<line>.*?)\): (Error|Warning): ',
                                IGNORECASE)


def process_xml2rfc_log(output, filename):
    '''Process xml2rfc output and return dictionary of errors and warnings'''
    log = []
    errors = []
    warnings = []
    unicode = []

    if output.stderr:
        log = cleanup_output(filename,
                             output.stderr.decode(
                                 'utf-8', errors='ignore')).split('\n')

    for entry in log:
        error = XML2RFC_ERROR_REGEX.search(entry)
        warning = XML2RFC_WARN_REGEX.search(entry)
        line = XML2RFC_LINE_NUMBER_REGEX.search(entry)
        if error and (message := error.group('message')):
            if line and (line := line.group('line')):
                errors.append(f'({line}) {message}')
            else:
                errors.append(message)
        elif warning and (message := warning.group('message')):
            if 'Found non-ascii characters' in message:
                if line and (line := line.group('line')):
                    unicode.append(f'({line}) {message}')
                else:
                    warnings.append(message)
            else:
                if line and (line := line.group('line')):
                    warnings.append(f'({line}) {message}')
                else:
                    warnings.append(message)

    return {'errors': errors, 'warnings': warnings, 'bare_unicode': unicode}


def get_errors(output, filename):
    '''Returns errors as a string'''

    log = process_xml2rfc_log(output, filename)

    if len(log['errors']) > 0:
        return '\n'.join(log['errors'])
    else:
        return None


def update_logs(logs, new_entries):
    '''Adds new entries to logs'''
    if new_entries:
        logs['errors'].extend(new_entries['errors'])
        logs['warnings'].extend(new_entries['warnings'])

    return logs
