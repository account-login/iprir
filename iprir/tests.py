from ipaddress import IPv4Address, IPv6Address, IPv6Network
from contextlib import contextmanager
import tempfile
import os
import requests

import iprir
from iprir.record import RIRRecord
from iprir.parser import parse_file, parse_string
from iprir.database import DB
import iprir.updater


iprir.updater.initialize()
REAL_RECORDS = parse_file(iprir.TEXT_DB_PATH)

SAMPLE_TEXT_DB_CONTENT = '''
#
2|apnic|20170120|50186|19830613|20170119|+1000
apnic|*|asn|*|7517|summary
apnic|*|ipv4|*|36581|summary
apnic|*|ipv6|*|6088|summary
apnic|NZ|asn|681|1|20020801|allocated
apnic|AU|ipv4|1.0.0.0|256|20110811|assigned
apnic|CN|ipv4|1.0.1.0|256|20110414|allocated
apnic|CN|ipv6|2001:250::|35|20000426|allocated
apnic|CN|ipv6|2001:250:2000::|35|20020726|allocated
'''


@contextmanager
def patch(obj, key, value):
    origin = getattr(obj, key)
    setattr(obj, key, value)
    try:
        yield
    finally:
        setattr(obj, key, origin)


@contextmanager
def patch_db_path():
    fd, text_db_path = tempfile.mkstemp(prefix='iprir_test_', suffix='.txt')
    os.close(fd)
    fd, sql_db_path = tempfile.mkstemp(prefix='iprir_test_', suffix='.sqlite')
    os.close(fd)
    print('text_db_path', text_db_path)
    print('sql_db_path', sql_db_path)

    with patch(iprir, 'TEXT_DB_PATH', text_db_path):
        with patch(iprir, 'SQL_DB_PATH', sql_db_path):
            try:
                yield text_db_path, sql_db_path
            except Exception:
                raise
            else:
                os.remove(text_db_path)
                os.remove(sql_db_path)


def write_string_to_file(filename: str, string: str):
    with open(filename, 'wt') as fp:
        fp.write(string)


def test_record_ipv4():
    r = RIRRecord('CN', 'ipv4', '1.0.1.0', '256', 'assigned')
    assert r.length == 256
    assert r.ipv4.exploded == '1.0.1.0'
    assert r.ipv4_network.network_address == r.ipv4
    assert r.ipv4_network.prefixlen == 24
    assert r.ipv4 == IPv4Address(r.as_int)


def test_record_ipv6():
    r = RIRRecord('CN', 'ipv6', '2001:250::', '35', 'allocated')
    assert r.length == 2 ** (128 - 35)
    assert r.ipv6.compressed == '2001:250::'
    assert r.ipv6_network.network_address == r.ipv6
    assert r.ipv6_network.prefixlen == 35
    assert r.ipv6 == IPv6Address(r.as_int)


def test_parse():
    records = parse_string(SAMPLE_TEXT_DB_CONTENT)
    assert len(records) == 5
    r = records[-1]
    assert (r.country, r.ipv6, r.ipv6_network, r.status) == (
        'CN',
        IPv6Address('2001:250:2000::'),
        IPv6Network('2001:250:2000::/35'),
        'allocated'
    )


def test_ip_overlap():
    def verify(lst):
        lst.sort(key=lambda x: x[0])
        for i in range(1, len(lst)):
            prev_start, prev_len = lst[i - 1]
            assert prev_start + prev_len <= lst[i][0]

    lst4 = []
    lst6 = []
    for r in REAL_RECORDS:
        if r.type == 'ipv4':
            lst4.append((r.as_int, r.length))
        elif r.type == 'ipv6':
            lst6.append((r.as_int, r.length))

    verify(lst4)
    verify(lst6)


def test_db():
    with patch_db_path() as pathes:
        text_db_path, sql_db_path = pathes
        write_string_to_file(text_db_path, SAMPLE_TEXT_DB_CONTENT)
        records = parse_file(text_db_path)

        db = DB()
        try:
            ret = db.reset_table()
            assert ret
            ret = db.add_records(records)
            assert ret

            cn4 = db.by_country('ipv4', 'CN')
            assert len(cn4) == 1
            assert cn4[0] == records[2]

            cn6 = db.by_country('ipv6', 'CN')
            assert len(cn6) == 2
            assert cn6 == records[3:5]

            r = db.by_ip(IPv4Address('1.0.1.0'))
            assert r == records[2]
            r = db.by_ip(IPv4Address('1.0.1.255'))
            assert r == records[2]
            r = db.by_ip(IPv4Address('1.0.2.0'))
            assert r is None

            r = db.by_ip(IPv6Address('2001:250::'))
            assert r == records[3]
            net = records[3].ipv6_network
            r = db.by_ip(net.network_address + net.num_addresses)
            assert r == records[4]
            net = records[4].ipv6_network
            r = db.by_ip(net.network_address + net.num_addresses)
            assert r is None
        finally:
            db.close()


def test_update():
    def fake_get(*args, **kwargs):
        class Obj:
            pass
        o = Obj()
        o.text = SAMPLE_TEXT_DB_CONTENT
        return o

    with patch(requests, 'get', fake_get):
        with patch_db_path():
            iprir.updater.update()
            db = DB()
            try:
                assert db.all() == parse_string(SAMPLE_TEXT_DB_CONTENT)
            finally:
                db.close()
