from logging import getLogger

from at.utils.runner import proc_run, RunnerError


def validate_yang(filename, ietf=True, verbose=True, strict=False, logger=getLogger()):
    """Validate YANG files with pyang"""
    logger.debug("running pyang")
    output = None

    args = ["pyang"]
    if ietf:
        args.append("--ietf")
    if verbose:
        args.append("--verbose")
    if strict:
        args.append("--strict")
    args.append(filename)

    try:
        output = proc_run(args=args, capture_output=True)
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
