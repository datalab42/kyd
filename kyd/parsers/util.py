import os
import zipfile
import logging

from textparser import PortugueseRulesParser, GenericParser


class PortugueseRulesParser2(PortugueseRulesParser):
    def parseInteger(self, text, match):
        r"^\d+$"
        return int(match.group())

    def parseND(self, text, match):
        r"^N\/D$"
        return None

    def parseEmpty(self, text, match):
        r"^$"
        return None

    def parseEmpty2(self, text, match):
        r"^--$"
        return None

    def parseDate_ptBR(self, text, match):
        r"(\d{2})/(\d{2})/(\d{4})"
        return "{}-{}-{}".format(match.group(3), match.group(2), match.group(1))

    def parseDate_YYYYMMDD(self, text, match):
        r"(\d{4})(\d{2})(\d{2})"
        return "{}-{}-{}".format(match.group(1), match.group(2), match.group(3))


def convert_csv_to_dict(file, sep=";", encoding="utf-8"):
    parser = GenericParser()
    for ix, line in enumerate(file):
        line = line.decode(encoding).strip()
        if ix == 0:
            hdr = [field.lower() for field in line.split(sep)]
        vals = [parser.parse(val) for val in line.split(sep)]
        yield dict(zip(hdr, vals))


def read_fwf(con, widths, colnames=None, skip=0, parse_fun=lambda x: x):
    """read and parse fixed width field files"""
    colpositions = []
    x = 0
    line_len = sum(widths)
    for w in widths:
        colpositions.append((x, x + w))
        x = x + w

    colnames = (
        ["V{}".format(ix + 1) for ix in range(len(widths))]
        if colnames is None
        else colnames
    )

    terms = []
    for ix, line in enumerate(con):
        if ix < skip:
            continue
        line = line.strip()
        if len(line) != line_len:
            continue
        fields = [line[dx[0] : dx[1]].strip() for dx in colpositions]
        obj = dict((k, v) for k, v in zip(colnames, fields))
        terms.append(parse_fun(obj))

    return terms


def float_or_none(val):
    """Converts val to float or returns None if it's not possible."""
    try:
        return float(val)
    except:
        return None


def str_or_none(val):
    return str(val) if val else None


def unzip_and_get_content(fname, index=-1, encode=False, encoding="latin1"):
    with open(fname, "rb") as temp:
        zf = zipfile.ZipFile(temp)
        name = zf.namelist()[index]
        logging.info("zipped file %s", name)
        content = zf.read(name)
        zf.close()
    # temp.close()
    if encode:
        return content.decode(encoding)
    else:
        return content


def unzip_to(fname, dest, index=-1):
    with open(fname, "rb") as temp:
        fp = unzip_file_to(temp, dest, index)

    return fp


def unzip_file_to(temp, dest, index=-1):
    zf = zipfile.ZipFile(temp)
    name = zf.namelist()[index]
    logging.info("zipped file %s", name)
    zf.extract(name, dest)
    zf.close()

    return os.path.join(dest, name)
