import os
import shutil
import requests
import itertools

import iprir
from iprir.parser import parse_file
from iprir.database import DB
from iprir.utils import get_logger


__all__ = ('update_text_db', 'update_sql_db', 'update', 'initialize',)


def update_text_db(which='all', *, timeout=30):
    if which == 'all':
        items = iprir.TEXT_DB_URLS.items()
    else:
        items = [(which, iprir.TEXT_DB_URLS[which])]

    for name, url in items:
        _update_text_db(url, iprir.TEXT_DB_PATH[name], timeout=timeout)


def _update_text_db(url, file, *, timeout=30):
    # TODO: record last modified date from server
    text = requests.get(url, timeout=timeout).text

    old_text_db_path = file + '.old'
    # backup
    db_exists = os.path.exists(file)
    if db_exists:
        get_logger().info('backup text db to %s', old_text_db_path)
        shutil.copyfile(file, old_text_db_path)

    try:
        with open(file, 'wt') as fp:
            fp.write(text)
    except:
        get_logger().error('update text db failed: %s', url)
        if db_exists:
            get_logger().info('revert to backup: %s', old_text_db_path)
            os.replace(old_text_db_path, file)
        raise
    else:
        get_logger().info('update text db succeeded: %s', url)
        if db_exists:
            os.unlink(old_text_db_path)


def update_sql_db():
    records = itertools.chain.from_iterable(map(parse_file, iprir.TEXT_DB_PATH.values()))
    # XXX: avoid conflicts, see iprir.tests:test_ip_overlap()
    records = filter(lambda r: r.country != 'AP', records)

    db = DB()
    try:
        ret = db.reset_table()
        assert ret
        ret = db.add_records(records)
        assert ret
    except Exception:
        get_logger().error('update sql db failed')
    else:
        get_logger().info('update sql db succeeded')
    finally:
        db.close()


def update(*, timeout=30):
    update_text_db(timeout=timeout)
    update_sql_db()


def initialize(*, timeout=30):
    is_init = all(map(os.path.exists, iprir.TEXT_DB_PATH.values()))
    if not is_init:
        update(timeout=timeout)
    elif not os.path.exists(iprir.SQL_DB_PATH):
        update_sql_db()


def main():
    from argparse import ArgumentParser

    parser = ArgumentParser(description='update RIR databases')
    parser.add_argument(
        'target', choices=['text', 'sql', 'all'], default='all', nargs='?',
        help='update text db, sqlite db or both',
    )
    parser.add_argument('-t', '--timeout', type=int, default=30)

    option = parser.parse_args()
    if option.target == 'text':
        update_text_db(timeout=option.timeout)
    elif option.target == 'sql':
        update_sql_db()
    elif option.target == 'all':
        update(timeout=option.timeout)
    else:
        assert not 'possible'


if __name__ == '__main__':
    main()
