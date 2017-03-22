import bisect

from iprir.database import DB
from iprir.record import RIRRecord, ip_to_int


__all__ = ('IpSet',)


class IpSet:
    def __init__(self, records):
        """
        :type records: list[iprir.record.RIRRecord]
        """
        assert records
        self.lo, self.hi, self.type = self.make_ranges(records)

    @staticmethod
    def make_ranges(records):
        lo = []
        hi = []
        rec_type = None
        for r in sorted(records, key=lambda x: x.as_int):   # type: RIRRecord
            if not lo:
                assert r.type in ('ipv4', 'ipv6')
                rec_type = r.type
                lo.append(r.as_int)
                hi.append(r.as_int + r.length)
            else:
                assert rec_type == r.type
                if r.as_int == hi[-1]:
                    hi[-1] = r.as_int + r.length
                else:
                    lo.append(r.as_int)
                    hi.append(r.as_int + r.length)

        assert len(lo) == len(hi) <= len(records)
        return lo, hi, rec_type

    def contains(self, ip):
        key = ip_to_int(ip)
        index = bisect.bisect_right(self.lo, key) - 1
        if index < 0 or not (self.lo[index] <= key < self.hi[index]):
            return False
        else:
            return True

    def __contains__(self, ip):
        return self.contains(ip)

    @classmethod
    def by_country(cls, type_: str, country: str) -> 'IpSet':
        db = DB()
        try:
            return cls(db.by_country(type_, country))
        finally:
            db.close()
