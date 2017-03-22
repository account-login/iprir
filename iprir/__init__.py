import logging
import os
import sys

import iprir.api
from iprir.api import *
from iprir.utils import set_logger


__version__ = '0.3.0.dev0'
__all__ = tuple(iprir.api.__all__)


MODULE_PATH = os.path.dirname(__file__)
SQL_DB_PATH = os.path.join(MODULE_PATH, 'iprir.sqlite')
TEXT_DB_URLS = dict(
    afrinic='https://ftp.apnic.net/stats/afrinic/delegated-afrinic-extended-latest',
    apnic='https://ftp.apnic.net/stats/apnic/delegated-apnic-extended-latest',
    arin='https://ftp.apnic.net/stats/arin/delegated-arin-extended-latest',
    lactic='https://ftp.apnic.net/stats/lacnic/delegated-lacnic-extended-latest',
    ripencc='https://ftp.apnic.net/stats/ripe-ncc/delegated-ripencc-extended-latest',
)
TEXT_DB_PATH = {
    name: os.path.join(MODULE_PATH, name + '.txt')
    for name in TEXT_DB_URLS.keys()
}


logger = logging.getLogger(__name__)
set_logger(logger)


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
