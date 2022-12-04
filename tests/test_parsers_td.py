
from kyd.parsers.td import TesouroDiretoHistoricalDataParser


def test_TesouroDiretoHistoricalDataParser():
    x = TesouroDiretoHistoricalDataParser('data/LFT_2022.xls')
    assert len(x.data) > 0
