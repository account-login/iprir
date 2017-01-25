from io import StringIO

from iprir.record import RIRRecord


# ref: http://ftp.apnic.net/apnic/stats/apnic/README.TXT


__all__ = ('parse_string', 'parse_file', 'parse_iter',)


def st_version(line: str):
    return st_sumary, None


def st_sumary(line: str):
    if line.endswith('summary'):
        return st_sumary, None
    else:
        return st_record(line)


def st_record(line: str):
    registry, cc, type_, start, value, date, status, *ext = line.split('|')
    record = RIRRecord(cc, type_, start, value, status)
    return st_record, record


def parse_iter(lines):
    status = st_version
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            status, result = status(line)
            if result is not None:
                yield result


def parse(lines):
    return list(parse_iter(lines))


def parse_file(filename):
    with open(filename, 'rt') as fp:
        return parse(fp)


def parse_string(string):
    lines = StringIO(string)
    return parse(lines)
