
from kyd.parsers import unzip_and_get_content
from kyd.parsers.b3 import CDIIDI, BVBG028, BVBG086, TaxaSwap
from kyd.parsers.b3 import COTAHIST_file

def test_CDIIDI():
    with open('data/CDIIDI_2019-09-22.json') as fp:
        rawdata = fp.read()
    x = CDIIDI(rawdata)
    assert x.data[0]['last_price'] == 5.4
    assert isinstance(x.data[0]['refdate'], str)
    assert x.data[0]['refdate'] == '2019-09-20'
    assert x.data[0]['symbol'] == 'CDI'
    assert len(x.data) == 2


def test_BVBG028():
    rawdata = unzip_and_get_content('data/IN210423.zip')
    x = BVBG028(rawdata)
    assert len(x.data) > 0


def test_BVBG086():
    rawdata = unzip_and_get_content('data/PR210423.zip')
    x = BVBG086(rawdata)
    assert len(x.data) > 0


def test_TaxaSwap():
    rawdata = unzip_and_get_content('data/TS190910.ex_', encode=True)
    x = TaxaSwap(rawdata)
    assert len(x.data) > 0


import inspect

def test_fwf():
    ch = COTAHIST_file('data/COTAHIST_A2020_TEST.TXT')
    # ms = inspect.getmembers(ch)
    # ms = dir(ch)
    print(ch.header)

