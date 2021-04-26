
from kyd.parsers import unzip_and_get_content

def test_unzip():
    rawdata = unzip_and_get_content('data/IR210423.zip')
    assert rawdata is not None

    rawdata = unzip_and_get_content('data/TS190910.ex_')
    assert rawdata is not None

