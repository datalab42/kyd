
import csv
from datetime import datetime
from itertools import dropwhile
from io import StringIO

import lxml.html

from . import PortugueseRulesParser2


class AnbimaTPF:
    def __init__(self, fname):
        self.fname = fname
        self.instruments = []
        self.pp = PortugueseRulesParser2()
        self.parse()

    def parse(self):
        if isinstance(self.fname, str):
            with open(self.fname, 'r', encoding='ISO-8859-1') as fp:
                self._parse(fp)
        else:
            self._parse(self.fname)

    def _parse(self, fp):
        _drop_first_n = dropwhile(lambda x: x[0] < 3, enumerate(fp))
        _drop_empy = filter(lambda x: x[1].strip() != '', _drop_first_n)
        for _, line in _drop_empy:
            row = line.split('@')
            tit = dict(
                symbol=row[0],
                refdate=self.pp.parse(row[1]),
                cod_selic=row[2],
                issue_date=self.pp.parse(row[3]),
                maturity_date=self.pp.parse(row[4]),
                bid_yield=self.pp.parse(row[5]),
                ask_yield=self.pp.parse(row[6]),
                ref_yield=self.pp.parse(row[7]),
                price=self.pp.parse(row[8])
            )
            self.instruments.append(tit)


    @property
    def data(self):
        return self.instruments


def parse_titpub(text, buf):
    pp = PortugueseRulesParser2()
    text = StringIO(text.decode('ISO-8859-1'))
    writer = csv.writer(buf)
    _drop_first_2 = dropwhile(lambda x: x[0] < 2, enumerate(text))
    _drop_empy = filter(lambda x: x[1].strip() != '', _drop_first_2)
    for c, line in _drop_empy:
        row = line.split('@')
        tit = dict(
            titulo=row[0],
            data_referencia=row[1],
            codigo_selic=row[2],
            data_base=row[3],
            data_vencimento=row[4],
            taxa_compra=pp.parse(row[5]),
            taxa_venda=pp.parse(row[6]),
            taxa_ind=pp.parse(row[7]),
            pu=pp.parse(row[8])
        )
        writer.writerow(tit.values())
    date_str = datetime.strptime(tit['data_referencia'], '%Y%m%d').strftime('%Y-%m-%d')
    return date_str


def parse_vnataxatitpub(text, buf):
    pp = PortugueseRulesParser2()
    writer = csv.writer(buf)
    writer.writerow(['data_ref', 'taxa', 'valor', 'projecao', 'vigencia'])

    root = lxml.html.fromstring(text.decode('ISO-8859-1'))
    
    sel = "div#listaNTN-B > center > table > tr:nth-child(2) > td:nth-child(2)"
    date = root.cssselect(sel)[0].text_content()
    sel = "div#listaNTN-B > center > table > tr:nth-child(4) > td:nth-child(3)"
    value = root.cssselect(sel)[0].text_content()
    sel = "div#listaNTN-B > center > table > tr:nth-child(4) > td:nth-child(4)"
    projecao = root.cssselect(sel)[0].text_content()
    sel = "div#listaNTN-B > center > table > tr:nth-child(4) > td:nth-child(5)"
    vigencia = root.cssselect(sel)[0].text_content()
    writer.writerow([pp.parse(date), 'IPCA', pp.parse(value), projecao, pp.parse(vigencia)])
    
    sel = "div#listaNTN-C > center > table > tr:nth-child(2) > td:nth-child(2)"
    date = root.cssselect(sel)[0].text_content()
    sel = "div#listaNTN-C > center > table > tr:nth-child(4) > td:nth-child(3)"
    value = root.cssselect(sel)[0].text_content()
    sel = "div#listaNTN-C > center > table > tr:nth-child(4) > td:nth-child(4)"
    projecao = root.cssselect(sel)[0].text_content()
    sel = "div#listaNTN-C > center > table > tr:nth-child(4) > td:nth-child(5)"
    vigencia = root.cssselect(sel)[0].text_content()
    writer.writerow([pp.parse(date), 'IGPM', pp.parse(value), projecao, pp.parse(vigencia)])
    
    sel = "div#listaLFT > center > table > tr:nth-child(2) > td:nth-child(2)"
    date = root.cssselect(sel)[0].text_content()
    sel = "div#listaLFT > center > table > tr:nth-child(4) > td:nth-child(3)"
    value = root.cssselect(sel)[0].text_content()
    writer.writerow([pp.parse(date), 'SELIC', pp.parse(value), None, None])

    return pp.parse(date)


def parse_vnatitpub(text, buf):
    pp = PortugueseRulesParser2()
    writer = csv.writer(buf)
    writer.writerow(['data_ref', 'titulo', 'VNA'])

    root = lxml.html.fromstring(text.decode('ISO-8859-1'))
    
    sel = "div#listaNTN-B > center > table > tr:nth-child(2) > td:nth-child(2)"
    date = root.cssselect(sel)[0].text_content()
    sel = "div#listaNTN-B > center > table > tr:nth-child(4) > td:nth-child(2)"
    value = root.cssselect(sel)[0].text_content()
    writer.writerow([pp.parse(date), 'NTNB', pp.parse(value)])
    
    sel = "div#listaNTN-C > center > table > tr:nth-child(2) > td:nth-child(2)"
    date = root.cssselect(sel)[0].text_content()
    sel = "div#listaNTN-C > center > table > tr:nth-child(4) > td:nth-child(2)"
    value = root.cssselect(sel)[0].text_content()
    writer.writerow([pp.parse(date), 'NTNC', pp.parse(value)])
    
    sel = "div#listaLFT > center > table > tr:nth-child(2) > td:nth-child(2)"
    date = root.cssselect(sel)[0].text_content()
    sel = "div#listaLFT > center > table > tr:nth-child(4) > td:nth-child(2)"
    value = root.cssselect(sel)[0].text_content()
    writer.writerow([pp.parse(date), 'LFT', pp.parse(value)])

    return pp.parse(date)

