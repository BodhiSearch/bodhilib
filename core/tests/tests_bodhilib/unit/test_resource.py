from bodhilib import local_dir, local_file, url_resource, glob_pattern


def test_local_file(tmpdir):
  resource = local_file(f"{tmpdir}/test.txt")
  assert resource.resource_type == "local_file"
  assert resource.path == f"{tmpdir}/test.txt"
  assert resource.metadata == {"path": f"{tmpdir}/test.txt", "resource_type": "local_file"}


def test_local_dir(tmpdir):
  resource = local_dir(tmpdir, False, False)
  assert resource.resource_type == "local_dir"
  assert resource.path == tmpdir
  assert resource.metadata == {
    "path": tmpdir,
    "resource_type": "local_dir",
    "recursive": False,
    "exclude_hidden": False,
  }


def test_glob_pattern(tmpdir):
  pattern = "*.txt"
  resource = glob_pattern(str(tmpdir), pattern, True, True)
  assert resource.resource_type == "glob"
  assert resource.path == str(tmpdir)
  assert resource.pattern == "*.txt"
  assert resource.recursive is True
  assert resource.exclude_hidden is True
  assert resource.metadata == {
    "path": str(tmpdir),
    "pattern": pattern,
    "resource_type": "glob",
    "recursive": True,
    "exclude_hidden": True,
  }


def test_url_resource():
  url = "https://www.example.com"
  resource = url_resource(url)
  assert resource.resource_type == "url"
  assert resource.path == url
  assert resource.metadata == {"path": url, "resource_type": "url"}
