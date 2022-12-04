
from kyd.parsers.anbima import TPFParser, VnaTPFParser, DebenturesParser


def test_AnbimaTPF():
    x = TPFParser('data/ANBIMA_TPF_2019-01-02.txt')
    assert isinstance(x.data, list)
    assert len(x.data) > 0


def test_AnbimaVnaTPF():
    x = VnaTPFParser('data/ANBIMA_TPF_VNA_2019-01-06.html')
    assert isinstance(x.data, list)
    assert len(x.data) > 0


def test_AnbimaDebentures():
    x = DebenturesParser('data/deb_2021-04-20.txt')
    assert isinstance(x.data, list)
    assert len(x.data) > 0
