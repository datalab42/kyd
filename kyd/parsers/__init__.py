
import os
import re
import zipfile
import logging
from datetime import datetime
from collections import OrderedDict

from textparser import PortugueseRulesParser, GenericParser


class PortugueseRulesParser2(PortugueseRulesParser):
    def parseInteger(self, text, match):
        r'^\d+$'
        return int(match.group())

    def parseND(self, text, match):
        r'^N\/D$'
        return None

    def parseEmpty(self, text, match):
        r'^$'
        return None

    def parseEmpty2(self, text, match):
        r'^--$'
        return None

    def parseDate_ptBR(self, text, match):
        r'(\d{2})/(\d{2})/(\d{4})'
        return '{}-{}-{}'.format(match.group(3), match.group(2), match.group(1))

    def parseDate_YYYYMMDD(self, text, match):
        r'(\d{4})(\d{2})(\d{2})'
        return '{}-{}-{}'.format(match.group(1), match.group(2), match.group(3))


def convert_csv_to_dict(file, sep=';', encoding='utf-8'):
    parser = GenericParser()
    for ix, line in enumerate(file):
        line = line.decode(encoding).strip()
        if ix == 0:
            hdr = [field.lower() for field in line.split(sep)]
        vals = [parser.parse(val) for val in line.split(sep)]
        yield dict(zip(hdr, vals))


def read_fwf(con, widths, colnames=None, skip=0, parse_fun=lambda x: x):
    '''read and parse fixed width field files'''
    colpositions = []
    x = 0
    line_len = sum(widths)
    for w in widths:
        colpositions.append((x, x+w))
        x = x + w

    colnames = ['V{}'.format(ix+1) for ix in range(len(widths))] if colnames is None else colnames

    terms = []
    for ix, line in enumerate(con):
        if ix < skip:
            continue
        line = line.strip()
        if len(line) != line_len:
            continue
        fields = [line[dx[0]:dx[1]].strip() for dx in colpositions]
        obj = dict((k, v) for k, v in zip(colnames, fields))
        terms.append(parse_fun(obj))
    
    return terms


def float_or_none(val):
    '''Converts val to float or returns None if it's not possible.'''
    try:
        return float(val)
    except:
        return None


def str_or_none(val):
    return str(val) if val else None


def unzip_and_get_content(fname, index=-1, encode=False, encoding='latin1'):
    with open(fname, 'rb') as temp:
        zf = zipfile.ZipFile(temp)
        name = zf.namelist()[index]
        logging.info('zipped file %s', name)
        content = zf.read(name)
        zf.close()
    # temp.close()
    if encode:
        return content.decode(encoding)
    else:
        return content


def unzip_to(fname, dest, index=-1):
    with open(fname, 'rb') as temp:
        fp = unzip_file_to(temp, dest, index)

    return fp


def unzip_file_to(temp, dest, index=-1):
    zf = zipfile.ZipFile(temp)
    name = zf.namelist()[index]
    logging.info('zipped file %s', name)
    zf.extract(name, dest)
    zf.close()

    return os.path.join(dest, name)


class Field:
    _counter = 0

    def __init__(self, width):
        self.width = width
        self._counter_val = Field._counter
        Field._counter += 1

    def parse(self, text):
        return text


class DateField(Field):
    def __init__(self, width, format):
        super(DateField, self).__init__(width)
        self.format = format

    def parse(self, text):
        return datetime.strptime(text, self.format)


class NumericField(Field):
    def __init__(self, width, dec=0, sign=''):
        super(NumericField, self).__init__(width)
        self.dec = dec
        self.sign = sign

    def parse(self, text):
        text = self.sign + text
        return float(text)/(10**int(self.dec))


class FWFRowMeta(type):
    """The metaclass for the FWFRow class. We use the metaclass to sort of
    the columns defined in the table declaration.
    """

    def __new__(meta, name, bases, attrs):
        """Create the class as normal, but also iterate over the attributes
        set.
        """
        cls = type.__new__(meta, name, bases, attrs)
        cls._fields = OrderedDict()
        # Then add the columns from this class.
        sorted_fields = sorted(
            ((k, v) for k, v in attrs.items() if isinstance(v, Field)),
            key=lambda x: x[1]._counter_val)
        cls._fields.update(OrderedDict(sorted_fields))
        return cls


class FWFRow(metaclass=FWFRowMeta):
    def __init__(self):
        self.pattern = re.compile(self._pattern)
        self.names = list(self._fields.keys())
        self.widths = [self._fields[n].width for n in self._fields]
        self.row_len = sum(self.widths)
        self.colpositions = []
        x = 0
        for fn in self._fields:
            f = self._fields[fn]
            w = f.width
            self.colpositions.append((x, x+w, f.parse))
            x = x + w

    def __len__(self):
        return self.row_len


class FWFFileMeta(type):
    """The metaclass for the FWFRow class. We use the metaclass to sort of
    the columns defined in the table declaration.
    """

    def __new__(meta, name, bases, attrs):
        """Create the class as normal, but also iterate over the attributes
        set.
        """
        cls = type.__new__(meta, name, bases, attrs)
        cls._rows = [(k, v) for k, v in attrs.items() if isinstance(v, FWFRow)]
        cls._buckets = dict((r[0], []) for r in cls._rows)
        return cls


class FWFFile(metaclass=FWFFileMeta):
    skip_row = 0

    def __init__(self, fname, encoding='UTF8'):
        with open(fname, 'r', encoding=encoding) as fp:
            for ix, line in enumerate(fp):
                if ix < self.skip_row:
                    continue
                row_name, row_template = self._get_row_template(line)
                # TODO: define policy to discard unmatched lines and
                #       lines with parsing errors
                # if len(line) < len(row_template):
                #     continue
                fields = [dx[2](line[dx[0]:dx[1]].strip()) for dx in row_template.colpositions]
                obj = dict((k, v) for k, v in zip(row_template.names, fields))
                self._buckets[row_name].append(obj)

    def __getattribute__(self, name: str):
        buckets = super(FWFFile, self).__getattribute__('_buckets')
        if name in buckets:
            return buckets[name]
        else:
            return super(FWFFile, self).__getattribute__(name)

    def _get_row_template(self, line):
        for row in self._rows:
            m = row[1].pattern.match(line)
            if m:
                return row


# class TPF(CSVFile):
#     _skip = 3
#     symbol = Field(0)
#     refdate = DateField(1)
#     cod_selic = Field(2)
#     issue_date = DateField(3)
#     maturity_date = DateField(4)
#     bid_yield = NumericField(5)
#     ask_yield = NumericField(6)
#     ref_yield = NumericField(7)
#     price = NumericField(8)


# tpf = TPF(fname)