from lxml import etree


def smart_find(node, x, ns):
    try:
        return node.find(x, ns).text
    except:
        return None


class BVBG087Parser:
    ATTRS = {
        "IndxInf": {
            "ticker_symbol": "SctyInf/SctyId/TckrSymb",
            "security_id": "SctyInf/FinInstrmId/OthrId/Id",
            "security_proprietary": "SctyInf/FinInstrmId/OthrId/Tp/Prtry",
            "security_market": "SctyInf/FinInstrmId/PlcOfListg/MktIdrCd",
            "asset_desc": "AsstDesc",
            "settlement_price": "SttlmVal",
            "open_price": "SctyInf/OpngPric",
            "min_price": "SctyInf/MinPric",
            "max_price": "SctyInf/MaxPric",
            "average_price": "SctyInf/TradAvrgPric",
            "close_price": "SctyInf/ClsgPric",
            "last_price": "SctyInf/IndxVal",
            "oscillation_val": "SctyInf/OscnVal",
            "rising_shares_number": "RsngShrsNb",
            "falling_shares_number": "FlngShrsNb",
            "stable_shares_number": "StblShrsNb",
        },
        "IOPVInf": {
            "ticker_symbol": "SctyId/TckrSymb",
            "security_id": "FinInstrmId/OthrId/Id",
            "security_proprietary": "FinInstrmId/OthrId/Tp/Prtry",
            "security_market": "FinInstrmId/PlcOfListg/MktIdrCd",
            "open_price": "OpngPric",
            "min_price": "MinPric",
            "max_price": "MaxPric",
            "average_price": "TradAvrgPric",
            "close_price": "ClsgPric",
            "last_price": "IndxVal",
            "oscillation_val": "OscnVal",
        },
        "BDRInf": {
            "ticker_symbol": "SctyId/TckrSymb",
            "security_id": "FinInstrmId/OthrId/Id",
            "security_proprietary": "FinInstrmId/OthrId/Tp/Prtry",
            "security_market": "FinInstrmId/PlcOfListg/MktIdrCd",
            "ref_price": "RefPric",
        },
    }

    def __init__(self, fname):
        self.fname = fname
        self.indexes = []
        self.parse()

    def parse(self):
        with open(self.fname, "rb") as fp:
            tree = etree.parse(fp)

        ns = {None: "urn:bvmf.218.01.xsd"}
        exchange = tree.getroot()[0][0]

        td_xpath = etree.ETXPath("//{urn:bvmf.218.01.xsd}TradDt")
        td = td_xpath(exchange)
        if len(td) > 0:
            trade_date = td[0].find("Dt", ns).text
        else:
            raise Exception("Invalid XML: tag TradDt not found")

        for tag in self.ATTRS:
            fields = self.ATTRS[tag]
            _xpath = etree.ETXPath("//{urn:bvmf.218.01.xsd}%s" % tag)
            for node in _xpath(exchange):
                data = {"trade_date": trade_date, "index_type": tag}
                for k in fields:
                    data[k] = smart_find(node, fields[k], ns)
                self.indexes.append(data)

    @property
    def data(self):
        return self.indexes
