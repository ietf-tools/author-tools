from subprocess import run

TIMEOUT = 120  # in seconds


# Exception
class RunnerError(Exception):
    """Error class for process runner"""

    pass


def proc_run(args, timeout=TIMEOUT, capture_output=True):
    """Return subprocess.run()"""
    try:
        return run(args, timeout=timeout, capture_output=True)
    except Exception:
        raise RunnerError(f"Error running {args[0]}.")
