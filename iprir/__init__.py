import pathlib
import logging
import os
import sys


_MODULE_PATH = pathlib.Path(__file__).parent
MODULE_PATH = str(_MODULE_PATH)
TEXT_DB_PATH = _MODULE_PATH.joinpath('delegated-apnic-latest').__str__()
SQL_DB_PATH = _MODULE_PATH.joinpath('apnic.sqlite').__str__()
TEXT_DB_URL = 'http://ftp.apnic.net/apnic/stats/apnic/delegated-apnic-latest'


logger = logging.getLogger(__name__)


def setup_logger():
    if os.environ.get('IPRIR_DEBUG') is not None:
        level = logging.DEBUG

        logging.basicConfig(stream=sys.stderr, level=level)
        logging.getLogger("requests").setLevel(logging.WARNING)

        # Initialize coloredlogs.
        try:
            import coloredlogs
        except ImportError:
            pass
        else:
            coloredlogs.install(level=level)

setup_logger()
