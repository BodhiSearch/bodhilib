import tempfile

import pytest
from bodhilib.data_loader import get_data_loader


def _tmpfile(tmpdir, filename, content):
    tmpfilepath = f"{tmpdir}/{filename}"
    tmpfile = open(tmpfilepath, "w")
    tmpfile.write(content)
    tmpfile.close()
    return tmpfilepath


def test_file_loader_loads_dir_recursively(tmpdir):
    _tmpfile(tmpdir, "test1.txt", "hello world!")
    tmpdir2 = tempfile.mkdtemp(dir=tmpdir)
    _tmpfile(tmpdir2, "test2.txt", "world hello!")

    # initialize file loader and add dir as resource with recusive=True
    file_loader = get_data_loader("file")
    file_loader.add_resource(dir=tmpdir, recursive=True)

    # iterate over documents and check if they are loaded correctly
    dociter = iter(file_loader)
    doc = next(dociter)
    assert doc.text == "hello world!"
    assert doc.metadata["filename"] == "test1.txt"
    assert doc.metadata["dirname"] == tmpdir
    doc = next(dociter)
    assert doc.text == "world hello!"
    assert doc.metadata["filename"] == "test2.txt"
    assert doc.metadata["dirname"] == tmpdir2

    with pytest.raises(StopIteration):
        next(dociter)


def test_file_loader_loads_all_files_in_dir(tmpdir):
    _tmpfile(tmpdir, "test1.txt", "hello world!")
    tmpdir2 = tempfile.mkdtemp(dir=tmpdir)
    _tmpfile(tmpdir2, "test2.txt", "world hello!")

    file_loader = get_data_loader("file")
    file_loader.add_resource(dir=tmpdir, recursive=False)

    dociter = iter(file_loader)
    doc = next(dociter)
    assert doc.text == "hello world!"
    assert doc.metadata["filename"] == "test1.txt"

    with pytest.raises(StopIteration):
        next(dociter)


def test_file_loader_loads_given_files(tmpdir):
    tmpfile1 = _tmpfile(tmpdir, "test1.txt", "hello world!")
    tmpfile2 = _tmpfile(tmpdir, "test2.txt", "world hello!")
    file_loader = get_data_loader("file")
    file_loader.add_resource(file=tmpfile1, recursive=False)
    file_loader.add_resource(file=tmpfile2, recursive=False)
    dociter = iter(file_loader)
    doc = next(dociter)
    assert doc.text == "hello world!"
    assert doc.metadata["filename"] == "test1.txt"
    assert doc.metadata["dirname"] == tmpdir
    doc = next(dociter)
    assert doc.text == "world hello!"
    assert doc.metadata["filename"] == "test2.txt"
    assert doc.metadata["dirname"] == tmpdir

    with pytest.raises(StopIteration):
        next(dociter)


def test_file_loader_loads_given_file(tmpdir):
    tmpfile1 = _tmpfile(tmpdir, "test1.txt", "hello world!")
    file_loader = get_data_loader("file")
    file_loader.add_resource(file=tmpfile1, recursive=False)
    dociter = iter(file_loader)
    doc = next(dociter)
    assert doc.text == "hello world!"
    assert doc.metadata["filename"] == "test1.txt"
    assert doc.metadata["dirname"] == tmpdir
    with pytest.raises(StopIteration):
        next(dociter)
