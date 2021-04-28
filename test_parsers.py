
from kyd.parsers import unzip_to
from kyd.parsers.b3 import CDIIDI, BVBG028, BVBG086, TaxaSwap
from kyd.parsers.b3 import COTAHIST

def test_CDIIDI():
    x = CDIIDI('data/CDIIDI_2019-09-22.json')
    assert x.data[0]['last_price'] == 5.4
    assert isinstance(x.data[0]['refdate'], str)
    assert x.data[0]['refdate'] == '2019-09-20'
    assert x.data[0]['symbol'] == 'CDI'
    assert len(x.data) == 2


def test_BVBG028():
    dest = unzip_to('data/IN210423.zip', 'data')
    x = BVBG028(dest)
    assert len(x.data) > 0


def test_BVBG086():
    dest = unzip_to('data/PR210423.zip', 'data')
    x = BVBG086(dest)
    assert len(x.data) > 0


def test_TaxaSwap():
    dest = unzip_to('data/TS190910.ex_', 'data')
    x = TaxaSwap(dest)
    assert len(x.data) > 0


def test_fwf():
    dest = unzip_to('data/COTAHIST_A1986.zip', 'data')
    x = COTAHIST(dest)
    assert len(x.data) > 0


def test_fwf_huge_files():
    x = COTAHIST('data/COTAHIST_A2020.TXT')
    assert len(x.data) > 0

