from logging import getLogger

from at.utils.runner import proc_run, RunnerError


def extract_abnf(filename, logger=getLogger()):
    """Extract ABNF using BAP aex"""
    logger.debug("running bap aex")
    output = None

    try:
        output = proc_run(args=["aex", filename], capture_output=True)
    except RunnerError as e:  # pragma: no cover
        logger.info(f"process error: {str(e)}")
    result = ""

    if output and output.stderr:
        error = output.stderr.decode("utf-8")
        result += error
        logger.info("bap aex error: {}".format(error))

    if output and output.stdout:
        result += output.stdout.decode("utf-8", errors="ignore")

    if result == "":
        result = "No output from BAP aex."

    return result


def parse_abnf(filename, logger=getLogger()):
    """Parse ABNF using BAP"""
    logger.debug("running bap")
    output = None

    try:
        output = proc_run(args=["bap", filename], capture_output=True)
    except RunnerError as e:  # pragma: no cover
        logger.info(f"process error: {str(e)}")

    errors = ""
    abnf = ""

    if output and output.stderr:
        errors = output.stderr.decode("utf-8").replace(filename, "")

    if output and output.stdout:
        abnf = output.stdout.decode("utf-8", errors="ignore")

    return (errors, abnf)
