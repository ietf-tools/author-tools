from logging import getLogger

from at.utils.runner import proc_run, RunnerError


def validate_yang(filename, logger=getLogger()):
    """Validate YANG files with pyang"""
    logger.debug("running pyang")
    output = None

    try:
        output = proc_run(args=["pyang", "--ietf", filename], capture_output=True)
    except RunnerError as e:  # pragma: no cover
        logger.info(f"process error: {str(e)}")

    errors = ""
    pyang = ""

    if output and output.stderr:
        errors = output.stderr.decode("utf-8", errors="ignore").replace(filename, "")

    if output and output.stdout:
        pyang = output.stdout.decode("utf-8", errors="ignore")

    if not errors and not pyang:
        pyang = "YANG file is valid."

    return (pyang, errors)
