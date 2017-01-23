import logging
import os
import sys


__version__ = '0.1.0.dev0'


MODULE_PATH = os.path.dirname(__file__)
TEXT_DB_PATH = os.path.join(MODULE_PATH, 'delegated-apnic-latest')
SQL_DB_PATH = os.path.join(MODULE_PATH, 'apnic.sqlite')
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
