import sqlite3
from ipaddress import IPv4Address, IPv6Address

import iprir
from iprir.utils import get_logger
from iprir.record import RIRRecord, ip_to_key


class DB:
    __CREATE_TALBLE__ = '''
        CREATE TABLE IF NOT EXISTS iprir (
            country CHAR(2) NOT NULL,
            type CHAR(4) NOT NULL,
            start TEXT NOT NULL,
            value TEXT NOT NULL,
            status CHAR(9) NOT NULL,
            ipv4_key_start CHAR(8) UNIQUE,
            ipv4_key_stop CHAR(8) UNIQUE,
            ipv6_key_start CHAR(32) UNIQUE,
            ipv6_key_stop CHAR(32) UNIQUE
        );
    '''

    def __init__(self):
        self.conn = sqlite3.connect(iprir.SQL_DB_PATH)
        self.cursor = self.conn.cursor()

    def reset_table(self, *, upgrade=False):
        cur = self.conn.cursor()
        try:
            if upgrade:
                cur.execute('DROP TABLE IF EXISTS iprir')
            cur.execute(self.__CREATE_TALBLE__)
            if not upgrade:
                cur.execute('DELETE FROM iprir')
            self.conn.commit()
        except sqlite3.Error:
            get_logger().exception('DB.reset_table(%s) failed', upgrade)
            self.conn.rollback()
            return False
        else:
            return True

    def add_records(self, records):
        try:
            self.conn.cursor().executemany(
                'INSERT INTO iprir VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (self.record_to_tuple(r) for r in records if self.filter_record(r)),
            )
            self.conn.commit()
        except sqlite3.Error:
            get_logger().exception('DB.add_records() failed')
            self.conn.rollback()
            return False
        else:
            return True

    @classmethod
    def record_to_tuple(cls, record: RIRRecord):
        tup = (record.country, record.type, record.start, record.value, record.status)
        if record.type == 'ipv4':
            tup += (record.ipv4_key_start, record.ipv4_key_stop, None, None)
        elif record.type == 'ipv6':
            tup += (None, None, record.ipv6_key_start, record.ipv6_key_stop)
        else:
            tup += (None, None, None, None)

        return tup

    @staticmethod
    def filter_record(record: RIRRecord):
        """Only add allocated or assigned record to database to avoid primary key conflicts."""
        return record.status in ('allocated', 'assigned') \
            and record.type in ('ipv4', 'ipv6')

    def all(self):
        cur = self.conn.cursor()
        cur.execute('SELECT * from iprir')
        return [self.tuple_to_record(tup) for tup in cur.fetchall()]

    def by_country(self, type_: str, country: str):
        cur = self.conn.cursor()
        cur.execute(
            'SELECT * from iprir WHERE type = :type AND country = :country',
            dict(type=type_, country=country),
        )
        return [self.tuple_to_record(tup) for tup in cur.fetchall()]

    def by_ip(self, ipobj):
        if isinstance(ipobj, IPv4Address):
            stmt = """
                SELECT * from iprir WHERE type = 'ipv4'
                    AND ipv4_key_start <= :ipkey AND :ipkey < ipv4_key_stop"""
        elif isinstance(ipobj, IPv6Address):
            stmt = """
                SELECT * from iprir WHERE type = 'ipv6'
                    AND ipv6_key_start <= :ipkey AND :ipkey < ipv6_key_stop"""
        else:
            raise ValueError('ipobj should be IPv4Address or IPv6Address')

        cur = self.conn.cursor()
        cur.execute(stmt, dict(ipkey=ip_to_key(ipobj)))
        result = cur.fetchall()
        assert len(result) <= 1
        if len(result) > 0:
            return self.tuple_to_record(result[0])
        else:
            return None

    @classmethod
    def tuple_to_record(cls, tup):
        return RIRRecord(*tup[:5])

    def close(self):
        self.conn.close()

    def __del__(self):
        self.close()
