
import os
import tempfile
from kyd.parsers import unzip_and_get_content, unzip_to

def test_unzip():
    rawdata = unzip_and_get_content('data/IR210423.zip')
    assert rawdata is not None

    rawdata = unzip_and_get_content('data/TS190910.ex_')
    assert rawdata is not None

    dest = unzip_to('data/TS190910.ex_', 'data')
    assert os.path.exists(dest)

    destdir = tempfile.gettempdir()
    dest = unzip_to('data/TS190910.ex_', destdir)
    assert os.path.exists(dest)