import json
import pandas as pd
from ..util import PortugueseRulesParser2


class CDIIDI:
    def __init__(self, fname):
        self.fname = fname
        self.parse()

    def parse(self):
        text_parser = PortugueseRulesParser2()
        with open(self.fname, "r") as fp:
            _data = json.loads(fp.read())
        cdi_data = {
            "refdate": text_parser.parse(_data["dataTaxa"]),
            "value": text_parser.parse(_data["taxa"]),
            "symbol": "CDI",
        }
        idi_data = {
            "refdate": text_parser.parse(_data["dataIndice"]),
            "value": text_parser.parse(_data["indice"]),
            "symbol": "IDI",
        }
        self._info = [cdi_data, idi_data]
        self._data = pd.DataFrame(self._info)

    @property
    def data(self):
        return self._data
