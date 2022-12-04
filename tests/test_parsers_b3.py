import os
import pandas as pd
from kyd.parsers.util import unzip_to
from kyd.parsers.b3 import CDIIDIParser, BVBG028Parser, BVBG086Parser, TaxaSwapParser, BVBG087Parser, COTAHISTParser, StockIndexInfoParser


def test_CDIIDI():
    x = CDIIDIParser('data/CDIIDI_2019-09-22.json')
    assert isinstance(x.data, list)
    assert x.data[0]['value'] == 5.4
    assert isinstance(x.data[0]['refdate'], str)
    assert x.data[0]['refdate'] == '2019-09-20'
    assert x.data[0]['symbol'] == 'CDI'
    assert len(x.data) == 2


def test_StockIndexInfoParser():
    x = StockIndexInfoParser('data/StockIndexInfo_2021-09-06.json')
    assert isinstance(x.data, pd.DataFrame)
    assert len(x.data) > 0


def test_BVBG028():
    dest = unzip_to('data/IN210423.zip', 'data')
    x = BVBG028Parser(dest)
    assert isinstance(x.data, list)
    assert len(x.data) > 0
    os.remove(dest)


def test_BVBG086():
    dest = unzip_to('data/PR210423.zip', 'data')
    x = BVBG086Parser(dest)
    assert isinstance(x.data, list)
    assert len(x.data) > 0
    os.remove(dest)


def test_TaxaSwap():
    dest = unzip_to('data/TS190910.ex_', 'data')
    x = TaxaSwapParser(dest)
    assert isinstance(x.data, list)
    assert len(x.data) > 0
    os.remove(dest)


def test_fwf():
    dest = unzip_to('data/COTAHIST_A1986.zip', 'data')
    x = COTAHISTParser(dest)
    assert isinstance(x.data, list)
    assert len(x.data) > 0
    os.remove(dest)


def test_BVBG087():
    dest = unzip_to('data/IR210423.zip', 'data')
    x = BVBG087Parser(dest)
    assert isinstance(x.data, list)
    assert len(x.data) > 0
    os.remove(dest)
