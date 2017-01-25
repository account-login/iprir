import os
import shutil
import requests

import iprir
from iprir.parser import parse_file
from iprir.database import DB


__all__ = ('update_text_db', 'update_sql_db', 'update', 'initialize',)


logger = iprir.logger


def update_text_db(*, timeout=30):
    # TODO: record last modified date from server
    text = requests.get(iprir.TEXT_DB_URL, timeout=timeout).text

    old_text_db_path = iprir.TEXT_DB_PATH + '.old'
    # backup
    db_exists = os.path.exists(iprir.TEXT_DB_PATH)
    if db_exists:
        logger.info('backup text db to %s', old_text_db_path)
        shutil.copyfile(iprir.TEXT_DB_PATH, old_text_db_path)

    try:
        with open(iprir.TEXT_DB_PATH, 'wt') as fp:
            fp.write(text)
    except:
        logger.error('update text db failed')
        if db_exists:
            logger.info('revert to backup')
            os.replace(old_text_db_path, iprir.TEXT_DB_PATH)
        raise
    else:
        logger.info('update text db successed')
        if db_exists:
            os.unlink(old_text_db_path)


def update_sql_db():
    records = parse_file(iprir.TEXT_DB_PATH)

    db = DB()
    try:
        ret = db.reset_table()
        assert ret
        ret = db.add_records(records)
        assert ret
    except Exception:
        logger.error('update sql db failed')
    else:
        logger.info('update sql db successed')
    finally:
        db.close()


def update(*, timeout=30):
    update_text_db(timeout=timeout)
    update_sql_db()


def initialize(*, timeout=30):
    if not os.path.exists(iprir.TEXT_DB_PATH):
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
