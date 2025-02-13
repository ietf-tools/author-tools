from logging import getLogger
from subprocess import run as proc_run, CalledProcessError

from weasyprint import __version__ as weasyprint_version
from xml2rfc import __version__ as xml2rfc_version


def get_kramdown_rfc_version(logger=getLogger()):
    """Return kramdown-rfc version"""

    output = proc_run(args=["kramdown-rfc", "--version"], capture_output=True)

    try:
        output.check_returncode()
        return output.stdout.decode("utf-8").replace("kramdown-rfc", "").strip()
    except CalledProcessError:  # pragma: no cover
        logger.info("kramdown-rfc error: {}".format(output.stderr.decode("utf-8")))
        return None


def get_mmark_version(logger=getLogger()):
    """Return mmark version"""

    output = proc_run(args=["mmark", "--version"], capture_output=True)

    try:
        output.check_returncode()
        return output.stdout.decode("utf-8").strip()
    except CalledProcessError:  # pragma: no cover
        logger.info("mmark error: {}".format(output.stderr.decode("utf-8")))
        return None


def get_id2xml_version(logger=getLogger()):
    """Return id2xml version"""

    output = proc_run(args=["id2xml", "--version"], capture_output=True)

    try:
        output.check_returncode()
        return output.stdout.decode("utf-8").replace("id2xml", "").strip()
    except CalledProcessError:  # pragma: no cover
        logger.info("id2xml error: {}".format(output.stderr.decode("utf-8")))
        return None


def get_xml2rfc_version():
    """Return xml2rfc version"""

    return xml2rfc_version


def get_weasyprint_version():
    """Return Weasyprint version"""

    return weasyprint_version


def get_idnits_version(logger=getLogger()):
    """Return idnits version"""

    output = proc_run(args=["idnits", "--version"], capture_output=True)

    try:
        output.check_returncode()
        return output.stdout.decode("utf-8").replace("idnits", "").strip()
    except CalledProcessError:  # pragma: no cover
        logger.info("idnits error: {}".format(output.stderr.decode("utf-8")))
        return None


def get_idnits3_version(logger=getLogger()):
    """Return idnits3 version"""

    output = proc_run(args=["idnits3", "--version"], capture_output=True)

    try:
        output.check_returncode()
        return output.stdout.decode("utf-8").replace("idnits3", "").strip()
    except CalledProcessError:  # pragma: no cover
        logger.info("idnits3 error: {}".format(output.stderr.decode("utf-8")))
        return None


def get_aasvg_version(logger=getLogger()):
    """Return aasvg version"""

    output = proc_run(args=["aasvg", "--version"], capture_output=True)

    try:
        output.check_returncode()
        return output.stdout.decode("utf-8").replace("aasvg", "").strip()
    except CalledProcessError:  # pragma: no cover
        logger.info("aasvg error: {}".format(output.stderr.decode("utf-8")))
        return None


def get_iddiff_version(logger=getLogger()):
    """Return iddiff version"""

    output = proc_run(args=["iddiff", "--version"], capture_output=True)

    try:
        output.check_returncode()
        return output.stdout.decode("utf-8").replace("iddiff", "").strip()
    except CalledProcessError:  # pragma: no cover
        logger.info("iddiff error: {}".format(output.stderr.decode("utf-8")))
        return None


def get_svgcheck_version(logger=getLogger()):
    """Return svgcheck version"""

    output = proc_run(args=["svgcheck", "--version"], capture_output=True)

    try:
        output.check_returncode()
        return (
            output.stdout.decode("utf-8")
            .split("\n")[0]
            .replace("svgcheck =", "")
            .strip()
        )
    except CalledProcessError:  # pragma: no cover
        logger.info("svgcheck error: {}".format(output.stderr.decode("utf-8")))
        return None


def get_rfcdiff_version(logger=getLogger()):
    """Return rfcdiff version"""

    output = proc_run(args=["rfcdiff", "--version"], capture_output=True)

    try:
        output.check_returncode()
        return (
            output.stdout.decode("utf-8").split("\n")[0].replace("rfcdiff", "").strip()
        )
    except CalledProcessError:  # pragma: no cover
        logger.info("rfcdiff error: {}".format(output.stderr.decode("utf-8")))
        return None


def get_rst2rfcxml_version(logger=getLogger()):
    """Return rst2rfcxml version"""

    output = proc_run(args=["rst2rfcxml", "--version"], capture_output=True)

    try:
        output.check_returncode()
        return (
            output.stdout.decode("utf-8")
            .split("\n")[0]
            .replace("rst2rfcxml", "")
            .strip()
        )
    except CalledProcessError:  # pragma: no cover
        logger.info("rst2rfcxml error: {}".format(output.stderr.decode("utf-8")))
        return None


if __name__ == "__main__":
    VERSION_INFORMATION = {
        "xml2rfc": get_xml2rfc_version(),
        "kramdown-rfc": get_kramdown_rfc_version(),
        "mmark": get_mmark_version(),
        "id2xml": get_id2xml_version(),
        "weasyprint": get_weasyprint_version(),
        "idnits": get_idnits_version(),
        "idnits3": get_idnits3_version(),
        "iddiff": get_iddiff_version(),
        "aasvg": get_aasvg_version(),
        "svgcheck": get_svgcheck_version(),
        "rfcdiff": get_rfcdiff_version(),
        "rst2rfcxml": get_rst2rfcxml_version(),
        "bap": "1.4",
    }  # bap does not provide a switch to get version
    print(f"VERSION_INFORMATION = {VERSION_INFORMATION}")
