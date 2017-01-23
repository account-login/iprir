import os
import shutil
import requests

import iprir
from iprir.parser import parse_file
from iprir.database import DB


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
    finally:
        db.close()


def update(*, timeout=32):
    update_text_db(timeout=timeout)
    update_sql_db()


def initialize(*, timeout=30):
    if not os.path.exists(iprir.TEXT_DB_PATH):
        update(timeout=timeout)
    elif not os.path.exists(iprir.SQL_DB_PATH):
        update_sql_db()
