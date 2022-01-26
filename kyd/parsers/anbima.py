
import re
import csv
from datetime import datetime
from itertools import dropwhile
from io import StringIO

import pandas as pd
import lxml.html
from lxml import etree

from . import PortugueseRulesParser2


class AnbimaTPF:
    def __init__(self, fname):
        self.fname = fname
        self.encoding = 'latin1'
        self.instruments = []
        self.pp = PortugueseRulesParser2()
        self.parse()

    def parse(self):
        with open(self.fname, 'r', encoding=self.encoding) as fp:
            self._parse(fp)

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


class AnbimaDebentures:
    def __init__(self, fname):
        self.fname = fname
        self.encoding = 'latin1'
        self.instruments = []
        self.pp = PortugueseRulesParser2()
        self.parse()

    def parse(self):
        with open(self.fname, 'r', encoding=self.encoding) as fp:
            self._parse(fp)

    def _parse(self, fp):
        # 0 Código@
        # 1 Nome@
        # 2 Repac./  Venc.@
        # 3 Índice/ Correção@
        # 4 Taxa de Compra@
        # 5 Taxa de Venda@
        # 6 Taxa Indicativa@
        # 7 Desvio Padrão@
        # 8 Intervalo Indicativo Minimo@
        # 9 Intervalo Indicativo Máximo@
        # 10 PU@
        # 11 % PU Par@
        # 12 Duration@
        # 13 % Reune@
        # 14 Referência NTN-B
        m = re.search(r'\d{4}-\d\d-\d\d', self.fname)
        refdate = m.group() if m else None
        _drop_first_n = dropwhile(lambda x: x[0] < 3, enumerate(fp))
        _drop_empy = filter(lambda x: x[1].strip() != '', _drop_first_n)
        for _, line in _drop_empy:
            row = line.strip().split('@')
            tit = dict(
                symbol=row[0],
                name=row[1],
                maturity_date=self.pp.parse(row[2]),
                underlying=row[3],
                bid_yield=self.pp.parse(row[4]),
                ask_yield=self.pp.parse(row[5]),
                ref_yield=self.pp.parse(row[6]),
                price=self.pp.parse(row[10]),
                perc_price_par=self.pp.parse(row[11]),
                duration=self.pp.parse(row[12]),
                perc_reune=self.pp.parse(row[13]),
                ref_ntnb=self.pp.parse(row[14]),
                refdate=refdate, # from filename
            )
            self.instruments.append(tit)
        self._data = pd.DataFrame(self.instruments)

    @property
    def data(self):
        return self._data


class AnbimaVnaTPF:
    def __init__(self, fname):
        self.fname = fname
        self.encoding = 'latin1'
        self.pp = PortugueseRulesParser2()
        self._data = []
        self.parse()

    def parse(self):
        with open(self.fname, 'r', encoding=self.encoding) as fp:
            parser = etree.HTMLParser()
            tree = etree.parse(fp, parser)
            self._data.append(self._parse_vna_node(tree, 'listaNTN-B'))
            self._data.append(self._parse_vna_node(tree, 'listaNTN-C'))
            self._data.append(self._parse_vna_node(tree, 'listaLFT'))

    def _parse_vna_node(self, tree, id):
        trs = tree.xpath(f"//div[@id='{id}']/*/table/tr")
        if len(trs) == 0:
            return {}
        instrument_ref = get_all_node_text(trs[0])
        date = get_all_node_text(trs[1][1])
        index_ref = get_all_node_text(trs[2][1])
        value = get_all_node_text(trs[3][1])
        rate_value = get_all_node_text(trs[3][2])
        try:
            projection = get_all_node_text(trs[3][3]) == 'P'
            rate_date = get_all_node_text(trs[3][4])
        except IndexError:
            projection = False
            rate_date = ''
        return {
            'refdate': self.pp.parse(date),
            'value': self.pp.parse(value),
            'rate': self.pp.parse(rate_value),
            'rate_start_date': self.pp.parse(rate_date),
            'proj': projection,
            'index_ref': index_ref,
            'instrument_ref': instrument_ref
        }

    @property
    def data(self):
        return [x for x in self._data if x]


def get_all_node_text(node):
    return ''.join(x.strip() for x in node.itertext())


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

