
import json
from itertools import groupby

import pandas as pd
from lxml import etree

from . import PortugueseRulesParser2, read_fwf, FWFFile, FWFRow, Field, DateField, NumericField

class TaxaSwap:
    widths = [6, 3, 2, 8, 2, 5, 15, 5, 5, 1, 14, 1, 5]
    colnames = [
        'id_transacao',
        'compl_transacao',
        'tipo_registro',
        'data_geracao_arquivo',
        'cod_curvas',
        'cod_taxa',
        'desc_taxa',
        'num_dias_corridos',
        'num_dias_saques',
        'sinal_taxa',
        'taxa_teorica',
        'carat_vertice',
        'cod_vertice'
    ]

    def __init__(self, fname):
        with open(fname, 'r') as fp:
            rawdata = fp.read()
            self.__data = read_fwf(rawdata.split('\n'), self.widths, self.colnames, parse_fun=self._parse)
        self.__findata = [self._build_findata(list(v)) for k, v in groupby(self.__data, key=lambda x: x['cod_taxa'])]
    
    def _parse(self, obj):
        obj['data_geracao_arquivo'] = '{}-{}-{}'.format(obj['data_geracao_arquivo'][:4], obj['data_geracao_arquivo'][4:6], obj['data_geracao_arquivo'][6:])
        obj['num_dias_corridos'] = int(obj['num_dias_corridos'])
        obj['num_dias_saques'] = int(obj['num_dias_saques'])
        obj['sinal_taxa'] = 1 if obj['sinal_taxa'] == '+' else -1
        obj['taxa_teorica'] = float(obj['taxa_teorica'])/1e7
        return obj

    def _build_findata(self, lst):
        taxa_teorica = [obj['taxa_teorica']*obj['sinal_taxa'] for obj in lst]
        num_dias_corridos = [obj['num_dias_corridos'] for obj in lst]
        num_dias_saques = [obj['num_dias_saques'] for obj in lst]
        carat_vertice = [obj['carat_vertice'] for obj in lst]
        keys = ('current_days', 'business_days', 'type', 'value')
        terms = [dict(zip(keys, x)) for x in zip(num_dias_corridos, num_dias_saques, carat_vertice, taxa_teorica)]

        return {
            'refdate': lst[0]['data_geracao_arquivo'],
            'id': lst[0]['cod_taxa'],
            'name': lst[0]['cod_curvas'],
            'description': lst[0]['desc_taxa'],
            'terms': terms
        }

    @property
    def data(self):
        return self.__data

    @property
    def findata(self):
        return self.__findata


class CDIIDI:
    def __init__(self, fname):
        self.fname = fname
        self.parse()

    def parse(self):
        text_parser = PortugueseRulesParser2()
        with open(self.fname, 'r') as fp:
            _data = json.loads(fp.read())
        cdi_data = {
            'refdate': text_parser.parse(_data['dataTaxa']),
            'last_price': text_parser.parse(_data['taxa']),
            'symbol': 'CDI'
        }
        idi_data = {
            'refdate': text_parser.parse(_data['dataIndice']),
            'last_price': text_parser.parse(_data['indice']),
            'symbol': 'IDI'
        }
        self._data = [cdi_data, idi_data]

    @property
    def data(self):
        return self._data


class BVBG028:
    ATTRS = {
        'header': {
            'trade_date': 'RptParams/RptDtAndTm/Dt',
            'security_id': 'FinInstrmId/OthrId/Id',
            'security_proprietary': 'FinInstrmId/OthrId/Tp/Prtry',
            'security_market': 'FinInstrmId/OthrId/PlcOfListg/MktIdrCd',
            'instrument_asset': 'FinInstrmAttrCmon/Asst',
            'instrument_asset_description': 'FinInstrmAttrCmon/AsstDesc',
            'instrument_market': 'FinInstrmAttrCmon/Mkt',
            'instrument_segment': 'FinInstrmAttrCmon/Sgmt',
            'instrument_description': 'FinInstrmAttrCmon/Desc'
        },
        'EqtyInf': {
            'security_category': 'InstrmInf/EqtyInf/SctyCtgy',
            'isin': 'InstrmInf/EqtyInf/ISIN',
            'distribution_id': 'InstrmInf/EqtyInf/DstrbtnId',
            'cfi_code': 'InstrmInf/EqtyInf/CFICd',
            'specification_code': 'InstrmInf/EqtyInf/SpcfctnCd',
            'corporation_name': 'InstrmInf/EqtyInf/CrpnNm',
            'symbol': 'InstrmInf/EqtyInf/TckrSymb',
            'payment_type': 'InstrmInf/EqtyInf/PmtTp',
            'allocation_lot_size': 'InstrmInf/EqtyInf/AllcnRndLot',
            'price_factor': 'InstrmInf/EqtyInf/PricFctr',
            'trading_start_date': 'InstrmInf/EqtyInf/TradgStartDt',
            'trading_end_date': 'InstrmInf/EqtyInf/TradgEndDt',
            'corporate_action_start_date': 'InstrmInf/EqtyInf/CorpActnStartDt',
            'ex_distribution_number': 'InstrmInf/EqtyInf/EXDstrbtnNb',
            'custody_treatment_type': 'InstrmInf/EqtyInf/CtdyTrtmntTp',
            'trading_currency': 'InstrmInf/EqtyInf/TradgCcy',
            'market_capitalisation': 'InstrmInf/EqtyInf/MktCptlstn',
            'last_price': 'InstrmInf/EqtyInf/LastPric',
            'first_price': 'InstrmInf/EqtyInf/FrstPric',
            'governance_indicator': 'InstrmInf/EqtyInf/GovnInd',
            'days_to_settlement': 'InstrmInf/EqtyInf/DaysToSttlm',
            'right_issue_price': 'InstrmInf/EqtyInf/RghtsIssePric',
        },
        'OptnOnEqtsInf': {
            'security_category': 'InstrmInf/OptnOnEqtsInf/SctyCtgy',
            'isin': 'InstrmInf/OptnOnEqtsInf/ISIN',
            'symbol': 'InstrmInf/OptnOnEqtsInf/TckrSymb',
            'exercise_price': 'InstrmInf/OptnOnEqtsInf/ExrcPric',
            'option_style': 'InstrmInf/OptnOnEqtsInf/OptnStyle',
            'expiration_date': 'InstrmInf/OptnOnEqtsInf/XprtnDt',
            'option_type': 'InstrmInf/OptnOnEqtsInf/OptnTp',
            'underlying_security_id': 'InstrmInf/OptnOnEqtsInf/UndrlygInstrmId/OthrId/Id',
            'underlying_security_proprietary': 'InstrmInf/OptnOnEqtsInf/UndrlygInstrmId/OthrId/Tp/Prtry',
            'underlying_security_market': 'InstrmInf/OptnOnEqtsInf/UndrlygInstrmId/OthrId/PlcOfListg/MktIdrCd',
            'protection_flag': 'InstrmInf/OptnOnEqtsInf/PrtcnFlg',
            'premium_upfront_indicator': 'InstrmInf/OptnOnEqtsInf/PrmUpfrntInd',
            'trading_start_date': 'InstrmInf/OptnOnEqtsInf/TradgStartDt',
            'trading_end_date': 'InstrmInf/OptnOnEqtsInf/TradgEndDt',
            'payment_type': 'InstrmInf/OptnOnEqtsInf/PmtTp',
            'allocation_lot_size': 'InstrmInf/OptnOnEqtsInf/AllcnRndLot',
            'price_factor': 'InstrmInf/OptnOnEqtsInf/PricFctr',
            'trading_currency': 'InstrmInf/OptnOnEqtsInf/TradgCcy',
            'days_to_settlement': 'InstrmInf/OptnOnEqtsInf/DaysToSttlm',
            'delivery_type': 'InstrmInf/OptnOnEqtsInf/DlvryTp',
            'automatic_exercise_indicator': 'InstrmInf/OptnOnEqtsInf/AutomtcExrcInd',
        },
        'FutrCtrctsInf': {
            'security_category': 'InstrmInf/FutrCtrctsInf/SctyCtgy',
            'expiration_date': 'InstrmInf/FutrCtrctsInf/XprtnDt',
            'symbol': 'InstrmInf/FutrCtrctsInf/TckrSymb',
            'expiration_code': 'InstrmInf/FutrCtrctsInf/XprtnCd',
            'trading_start_date': 'InstrmInf/FutrCtrctsInf/TradgStartDt',
            'trading_end_date': 'InstrmInf/FutrCtrctsInf/TradgEndDt',
            'value_type_code': 'InstrmInf/FutrCtrctsInf/ValTpCd',
            'isin': 'InstrmInf/FutrCtrctsInf/ISIN',
            'cfi_code': 'InstrmInf/FutrCtrctsInf/CFICd',
            'delivery_type': 'InstrmInf/FutrCtrctsInf/DlvryTp',
            'payment_type': 'InstrmInf/FutrCtrctsInf/PmtTp',
            'contract_multiplier': 'InstrmInf/FutrCtrctsInf/CtrctMltplr',
            'asset_settlement_indicator': 'InstrmInf/FutrCtrctsInf/AsstQtnQty',
            'allocation_lot_size': 'InstrmInf/FutrCtrctsInf/AllcnRndLot',
            'trading_currency': 'InstrmInf/FutrCtrctsInf/TradgCcy',
            'underlying_security_id': 'InstrmInf/FutrCtrctsInf/UndrlygInstrmId/OthrId/Id',
            'underlying_security_proprietary': 'InstrmInf/FutrCtrctsInf/UndrlygInstrmId/OthrId/Tp/Prtry',
            'underlying_security_market': 'InstrmInf/FutrCtrctsInf/UndrlygInstrmId/OthrId/PlcOfListg/MktIdrCd',
            'withdrawal_days': 'InstrmInf/FutrCtrctsInf/WdrwlDays',
            'working_days': 'InstrmInf/FutrCtrctsInf/WrkgDays',
            'calendar_days': 'InstrmInf/FutrCtrctsInf/ClnrDays',
        }
    }

    def __init__(self, fname):
        self.fname = fname
        self.instruments = []
        self.missing = set()
        self.parse()

    def parse(self):
        with open(self.fname, 'rb') as fp:
            tree = etree.parse(fp)
        exchange = tree.getroot()[0][0]
        ns = {None: 'urn:bvmf.052.01.xsd'}
        td_xpath = etree.ETXPath('//{urn:bvmf.052.01.xsd}BizGrpDtls')
        td = td_xpath(exchange)
        if len(td) > 0:
            self.creation_date = td[0].find('CreDtAndTm', ns).text[:10]
        else:
            raise Exception('Invalid XML: tag BizGrpDtls not found')

        xs = exchange.findall(
            '{urn:bvmf.052.01.xsd}BizGrp/{urn:bvmf.100.02.xsd}Document/{urn:bvmf.100.02.xsd}Instrm')
        for node in xs:
            self.parse_instrument_node(node)

    def parse_instrument_node(self, node):
        data = {'creation_date': self.creation_date}
        ns = {None: 'urn:bvmf.100.02.xsd'}
        for attr in self.ATTRS['header']:
            els = node.findall(self.ATTRS['header'][attr], ns)
            if len(els):
                data[attr] = els[0].text.strip()
        elm = node.findall('InstrmInf', ns)[0]
        # remove ns {urn:bvmf.100.02.xsd} = 21 chars
        tag = elm.getchildren()[0].tag[21:]
        if self.ATTRS.get(tag) is None:
            self.missing.add(tag)
            return
        for attr in self.ATTRS[tag]:
            els = node.findall(self.ATTRS[tag][attr], ns)
            if len(els):
                data[attr] = els[0].text.strip()
        data['instrument_type'] = tag
        self.instruments.append(data)

    @property
    def data(self):
        return self.instruments


class BVBG086:
    def __init__(self, fname):
        self.fname = fname
        self.instruments = []
        self.missing = set()
        self.parse()

    def parse(self):
        with open(self.fname, 'rb') as fp:
            tree = etree.parse(fp)
        exchange = tree.getroot()[0][0]
        ns = {None: 'urn:bvmf.052.01.xsd'}
        td_xpath = etree.ETXPath('//{urn:bvmf.052.01.xsd}BizGrpDtls')
        td = td_xpath(exchange)
        if len(td) > 0:
            self.creation_date = td[0].find('CreDtAndTm', ns).text[:10]
        else:
            raise Exception('Invalid XML: tag BizGrpDtls not found')

        xs = exchange.findall(
            '{urn:bvmf.052.01.xsd}BizGrp/{urn:bvmf.217.01.xsd}Document/{urn:bvmf.217.01.xsd}PricRpt')
        for node in xs:
            self.parse_price_report_node(node)

    def parse_price_report_node(self, node):
        attrs = {
            'trade_date': 'TradDt/Dt',
            'symbol': 'SctyId/TckrSymb',
            'security_id': 'FinInstrmId/OthrId/Id',  # SecurityId
            'security_proprietary': 'FinInstrmId/OthrId/Tp/Prtry',
            'security_market': 'FinInstrmId/PlcOfListg/MktIdrCd',
            'trade_quantity': 'TradDtls/TradQty',  # Negócios
            'volume': 'FinInstrmAttrbts/NtlFinVol',
            'open_interest': 'FinInstrmAttrbts/OpnIntrst',
            'traded_contracts': 'FinInstrmAttrbts/FinInstrmQty',
            'best_ask_price': 'FinInstrmAttrbts/BestAskPric',
            'best_bid_price': 'FinInstrmAttrbts/BestBidPric',
            'first_price': 'FinInstrmAttrbts/FrstPric',
            'min_price': 'FinInstrmAttrbts/MinPric',
            'max_price': 'FinInstrmAttrbts/MaxPric',
            'average_price': 'FinInstrmAttrbts/TradAvrgPric',
            'last_price': 'FinInstrmAttrbts/LastPric',
            # Negócios na sessão regular
            'regular_transactions_quantity': 'FinInstrmAttrbts/RglrTxsQty',
            # Contratos na sessão regular
            'regular_traded_contracts': 'FinInstrmAttrbts/RglrTraddCtrcts',
            # Volume financeiro na sessão regular
            'regular_volume': 'FinInstrmAttrbts/NtlRglrVol',
            # Negócios na sessão não regular
            'nonregular_transactions_quantity': 'FinInstrmAttrbts/NonRglrTxsQty',
            # Contratos na sessão não regular
            'nonregular_traded_contracts': 'FinInstrmAttrbts/NonRglrTraddCtrcts',
            # Volume financeiro na sessão nãoregular
            'nonregular_volume': 'FinInstrmAttrbts/NtlNonRglrVol',
            'oscillation_percentage': 'FinInstrmAttrbts/OscnPctg',
            'adjusted_quote': 'FinInstrmAttrbts/AdjstdQt',
            'adjusted_tax': 'FinInstrmAttrbts/AdjstdQtTax',
            'previous_adjusted_quote': 'FinInstrmAttrbts/PrvsAdjstdQt',
            'previous_adjusted_tax': 'FinInstrmAttrbts/PrvsAdjstdQtTax',
            'variation_points': 'FinInstrmAttrbts/VartnPts',
            'adjusted_value_contract': 'FinInstrmAttrbts/AdjstdValCtrct',
        }
        ns = {None: 'urn:bvmf.217.01.xsd'}
        data = {'creation_date': self.creation_date}
        for attr in attrs:
            els = node.findall(attrs[attr], ns)
            if len(els):
                data[attr] = els[0].text
        self.instruments.append(data)

    @property
    def data(self):
        return self.instruments


class COTAHIST_header(FWFRow):
    _pattern = r'^00'
    tipo_registro = Field(2)
    nome_arquivo = Field(13)
    cod_origem = Field(8)
    data_geracao_arquivo = DateField(8, '%Y%m%d')
    reserva = Field(214)


class COTAHIST_trailer(FWFRow):
    _pattern = r'^99'
    tipo_mercado = Field(2)
    nome_arquivo = Field(13)
    cod_origem = Field(8)
    data_geracao_arquivo = DateField(8, '%Y%m%d')
    num_registros = Field(11)
    reserva = Field(203)


class COTAHIST_histdata(FWFRow):
    _pattern = '^01'
    tipo_registro = Field(2)
    data_referencia = DateField(8, '%Y%m%d')
    cod_bdi = Field(2)
    cod_negociacao = Field(12)
    tipo_mercado = Field(3)
    nome_empresa = Field(12)
    especificacao = Field(10)
    num_dias_mercado_termo = Field(3)
    cod_moeda = Field(4)
    preco_abertura = NumericField(13, dec=2)
    preco_max = NumericField(13, dec=2)
    preco_min = NumericField(13, dec=2)
    preco_med = NumericField(13, dec=2)
    preco_ult = NumericField(13, dec=2)
    preco_melhor_oferta_compra = NumericField(13, dec=2)
    preco_melhor_oferta_venda = NumericField(13, dec=2)
    qtd_negocios = NumericField(5)
    qtd_titulos_negociados = NumericField(18)
    volume_titulos_negociados = NumericField(18, dec=2)
    preco_exercicio = NumericField(13, dec=2)
    indicador_correcao_preco_exercicio = Field(1)
    data_vencimento = DateField(8, '%Y%m%d')
    fator_cot = NumericField(7, dec=2)
    preco_exercicio_pontos = NumericField(13, dec=6)
    cod_isin = Field(12)
    num_dist = Field(3)


class COTAHIST_file(FWFFile):
    header = COTAHIST_header()
    trailer = COTAHIST_trailer()
    data = COTAHIST_histdata()


class COTAHIST:
    def __init__(self, fname):
        self.fname = fname
        self._data = None
        self.parse()

    def parse(self):
        self._data = COTAHIST_file(self.fname, encoding='latin1')

    @property
    def data(self):
        return self._data.data

    @property
    def header(self):
        return self._data.header

    @property
    def trailer(self):
        return self._data.trailer


def smart_find(node, x, ns):
    try:
        return node.find(x, ns).text
    except:
        return None


class BVBG087:
    ATTRS = {
        'IndxInf': {
            'ticker_symbol': 'SctyInf/SctyId/TckrSymb',
            'security_id': 'SctyInf/FinInstrmId/OthrId/Id',
            'security_proprietary': 'SctyInf/FinInstrmId/OthrId/Tp/Prtry',
            'security_market': 'SctyInf/FinInstrmId/PlcOfListg/MktIdrCd',
            'asset_desc': 'AsstDesc',
            'settlement_price': 'SttlmVal',
            'open_price': 'SctyInf/OpngPric',
            'min_price': 'SctyInf/MinPric',
            'max_price': 'SctyInf/MaxPric',
            'average_price': 'SctyInf/TradAvrgPric',
            'close_price': 'SctyInf/ClsgPric',
            'last_price': 'SctyInf/IndxVal',
            'oscillation_val': 'SctyInf/OscnVal',
            'rising_shares_number': 'RsngShrsNb',
            'falling_shares_number': 'FlngShrsNb',
            'stable_shares_number': 'StblShrsNb'
        },
        'IOPVInf': {
            'ticker_symbol': 'SctyId/TckrSymb',
            'security_id': 'FinInstrmId/OthrId/Id',
            'security_proprietary': 'FinInstrmId/OthrId/Tp/Prtry',
            'security_market': 'FinInstrmId/PlcOfListg/MktIdrCd',
            'open_price': 'OpngPric',
            'min_price': 'MinPric',
            'max_price': 'MaxPric',
            'average_price': 'TradAvrgPric',
            'close_price': 'ClsgPric',
            'last_price': 'IndxVal',
            'oscillation_val': 'OscnVal',
        },
        'BDRInf': {
            'ticker_symbol': 'SctyId/TckrSymb',
            'security_id': 'FinInstrmId/OthrId/Id',
            'security_proprietary': 'FinInstrmId/OthrId/Tp/Prtry',
            'security_market': 'FinInstrmId/PlcOfListg/MktIdrCd',
            'ref_price': 'RefPric',
        }
    }

    def __init__(self, fname):
        self.fname = fname
        self.indexes = []
        self.parse()

    def parse(self):
        with open(self.fname, 'rb') as fp:
            tree = etree.parse(fp)

        ns = {None: 'urn:bvmf.218.01.xsd'}
        exchange = tree.getroot()[0][0]

        td_xpath = etree.ETXPath('//{urn:bvmf.218.01.xsd}TradDt')
        td = td_xpath(exchange)
        if len(td) > 0:
            trade_date = td[0].find('Dt', ns).text
        else:
            raise Exception('Invalid XML: tag TradDt not found')

        for tag in self.ATTRS:
            fields = self.ATTRS[tag]
            _xpath = etree.ETXPath('//{urn:bvmf.218.01.xsd}%s' % tag)
            for node in _xpath(exchange):
                data = {
                    'trade_date': trade_date,
                    'index_type': tag
                }
                for k in fields:
                    data[k] = smart_find(node, fields[k], ns)
                self.indexes.append(data)

    @property
    def data(self):
        return self.indexes


class StockIndexInfo:
    def __init__(self, fname):
        self.fname = fname
        self._table = None
        self.parse()

    def parse(self):
        with open(self.fname) as fp:
            self._data = json.loads(fp.read())

        df = pd.DataFrame(self._data['results'])

        def _(dfx):
            indexes = dfx['indexes'].str.split(',').explode()
            return pd.DataFrame({
                'company': dfx['company'],
                'spotlight': dfx['spotlight'],
                'code': dfx['code'],
                'indexes': indexes,
            })

        dfr = (df.groupby(['company', 'spotlight', 'code'])
                 .apply(_)
                 .reset_index(drop=True))

        dfr['refdate'] = self._data['header']['update']
        dfr['duration_start_month'] = self._data['header']['startMonth']
        dfr['duration_end_month'] = self._data['header']['endMonth']
        dfr['duration_year'] = self._data['header']['year']

        dfr = dfr.rename(columns={
            'company': 'corporation_name',
            'spotlight': 'specification_code',
            'code': 'symbol'
        })

        self._table = dfr

    @property
    def data(self):
        return self._table