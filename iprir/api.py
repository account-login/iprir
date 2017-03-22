import iprir.database
import iprir.ipset


__all__ = ('get_db', 'by_ip', 'by_country')


_ipdb = None


def get_db():
    global _ipdb
    if _ipdb is None:
        _ipdb = iprir.database.DB()
    return _ipdb


def by_ip(ipobj):
    return get_db().by_ip(ipobj)


def by_country(type_, country):
    return iprir.ipset.IpSet.by_country(type_, country)
