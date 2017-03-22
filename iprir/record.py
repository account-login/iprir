import math
from collections import namedtuple
from ipaddress import IPv4Address, IPv4Network, IPv6Address, IPv6Network

from iprir.utils import cached_property


__all__ = ('RIRRecord', 'ip_to_int', 'ip_to_key')


# TODO: unify ipv4 and ipv6


class RIRRecord(namedtuple('RIRReord', ['country', 'type', 'start', 'value', 'status'])):
    """ref: https://www.arin.net/knowledge/statistics/nro_extended_stats_format.pdf"""

    @cached_property
    def length(self):
        if self.type == 'ipv4':
            return int(self.value)
        else:
            return 2 ** (128 - int(self.value))

    @cached_property
    def ipv4(self) -> IPv4Address:
        assert self.type == 'ipv4'
        return IPv4Address(self.start)

    @cached_property
    def ipv4_network(self) -> IPv4Network:
        assert self.type == 'ipv4'
        prefix = 32 - int(math.log2(int(self.value)))
        return IPv4Network('{self.start}/{prefix}'.format_map(locals()))

    @cached_property
    def ipv6(self) -> IPv6Address:
        assert self.type == 'ipv6'
        return IPv6Address(self.start)

    @cached_property
    def ipv6_network(self) -> IPv6Network:
        assert self.type == 'ipv6'
        prefix = int(self.value)
        return IPv6Network('{self.start}/{prefix}'.format_map(locals()))

    @cached_property
    def as_int(self) -> int:
        if self.type == 'ipv4':
            return ipv4_to_int(self.ipv4)
        elif self.type == 'ipv6':
            return ipv6_to_int(self.ipv6)
        else:
            assert not 'possible'

    @cached_property
    def ipv4_key_start(self) -> str:
        assert self.type == 'ipv4'
        return '%08x' % self.as_int

    @cached_property
    def ipv4_key_stop(self) -> str:
        assert self.type == 'ipv4'
        return '%08x' % (self.as_int + self.length)

    @cached_property
    def ipv6_key_start(self) -> str:
        assert self.type == 'ipv6'
        return '%032x' % self.as_int

    @cached_property
    def ipv6_key_stop(self) -> str:
        assert self.type == 'ipv6'
        return '%032x' % (self.as_int + self.length)


def ipv4_to_int(ip: IPv4Address):
    return int(''.join(map(lambda n: '%02x' % int(n), ip.exploded.split('.'))), base=16)


def ipv6_to_int(ip: IPv6Address):
    return int(ip.exploded.replace(':', ''), base=16)


def ip_to_int(ip) -> int:
    if isinstance(ip, IPv4Address):
        return ipv4_to_int(ip)
    elif isinstance(ip, IPv6Address):
        return ipv6_to_int(ip)
    else:
        raise ValueError('ip should be IPv4Address or IPv6Address')


def ip_to_key(ip) -> str:
    if isinstance(ip, IPv4Address):
        return '%08x' % ipv4_to_int(ip)
    elif isinstance(ip, IPv6Address):
        return '%032x' % ipv6_to_int(ip)
    else:
        raise ValueError('ip should be IPv4Address or IPv6Address')
