use lazy_static::lazy_static;
use pyo3::prelude::*;
use pyo3::types::PyList;
use regex::Regex;
use std::path::PathBuf;

lazy_static! {
  static ref HIDDEN_FILE: Regex = {
    let pattern = format!(r#".*\{}\.\w+.*"#, std::path::MAIN_SEPARATOR);
    Regex::new(&pattern).unwrap()
  };
}

#[pyfunction]
fn find_files(dir: String, pattern: String, hidden: bool, recursive: bool) -> PyResult<PyObject> {
  let result = _find_files(dir, pattern, hidden, recursive);
  match result {
    Ok(result) => Python::with_gil(|py| Ok(PyList::new(py, result).into_py(py))),
    Err(e) => Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e)),
  }
}

fn _find_files(dir: String, pattern: String, recursive: bool, hidden: bool) -> Result<Vec<String>, String> {
  let options = glob::MatchOptions {
    case_sensitive: true,
    require_literal_separator: false,
    require_literal_leading_dot: false,
  };
  let dir_path = PathBuf::from(dir);
  let pattern = if recursive {
    dir_path.join("**").join(pattern)
  } else {
    dir_path.join(pattern)
  };
  let pattern_str = pattern.to_str().ok_or("Invalid path").map_err(|e| e.to_string())?;
  let glob_result = glob::glob_with(pattern_str, options)
    .map_err(|e| format!("Glob error: {}", e))
    .map_err(|e| e.to_string())?;
  let result = glob_result
    .filter_map(Result::ok)
    .filter(|path| path.is_file() && (hidden || !HIDDEN_FILE.is_match(path.to_str().unwrap())))
    .map(|path| {
      let path_str = path.to_str().unwrap().to_owned();
      path_str
    })
    .collect::<Vec<_>>();
  Ok(result)
}

pub(crate) fn add_to_module(m: &PyModule) -> PyResult<()> {
  m.add_function(wrap_pyfunction!(find_files, m)?)?;
  Ok(())
}

#[cfg(test)]
mod test {
  use super::{_find_files, HIDDEN_FILE};
  use std::io::Write;
  use std::{fs::File, path::Path};

  struct Setup {
    temp_dir: tempfile::TempDir,
  }

  impl Setup {
    fn new() -> Self {
      let temp_dir = tempfile::Builder::new()
        .prefix("glob_test_")
        .tempdir()
        .expect("should create temp dir");
      create_files(temp_dir.path(), vec!["test1.txt", "test2.csv", ".test3.txt"]);
      let subdir = temp_dir.path().join("tmpdir2");
      std::fs::create_dir(&subdir).expect("failed to create subdir");
      create_files(&subdir, vec!["test4.txt", ".test5.txt"]);
      let hidden_subdir = temp_dir.path().join(".tmpdir3");
      std::fs::create_dir(&hidden_subdir).expect("failed to create subdir");
      create_files(&hidden_subdir, vec!["test6.txt", ".test7.txt"]);
      Setup { temp_dir }
    }

    fn path(&self) -> String {
      self.temp_dir.path().to_str().unwrap().to_string()
    }
  }

  fn create_files(inside: &Path, files: Vec<&str>) {
    for file in files {
      let mut file = File::create(inside.join(file)).expect("failed to create tempfile");
      writeln!(file, "hello world").unwrap();
    }
  }

  struct GlobTestHarness {}

  impl GlobTestHarness {
    fn run_test(&self, pattern: String, recursive: bool, hidden: bool, expected: Vec<&str>) {
      let setup = Setup::new();
      let test_dir = setup.path();
      let result = _find_files(test_dir.clone(), pattern, recursive, hidden);
      assert!(result.is_ok());
      let result = result.unwrap();
      let mut files = result
        .into_iter()
        .map(|path| path.trim_start_matches(&test_dir).to_owned())
        .collect::<Vec<_>>();
      files.sort();
      let expected = expected.into_iter().map(|path| path.to_owned()).collect::<Vec<_>>();
      assert_eq!(files, expected);
    }
  }

  #[test]
  fn test_glob_recursive_hidden_list() {
    let expected = vec![
      "/.test3.txt",
      "/.tmpdir3/.test7.txt",
      "/.tmpdir3/test6.txt",
      "/test1.txt",
      "/tmpdir2/.test5.txt",
      "/tmpdir2/test4.txt",
    ];
    GlobTestHarness {}.run_test("*.txt".to_string(), true, true, expected);
  }

  #[test]
  fn test_glob_not_recursive_hidden_list() {
    let expected = vec!["/.test3.txt", "/test1.txt"];
    GlobTestHarness {}.run_test("*.txt".to_string(), false, true, expected);
  }

  #[test]
  fn test_glob_recursive_not_hidden_list() {
    let expected = vec!["/test1.txt", "/tmpdir2/test4.txt"];
    GlobTestHarness {}.run_test("*.txt".to_string(), true, false, expected);
  }

  #[test]
  fn test_glob_not_recursive_not_hidden_list() {
    let expected = vec!["/test1.txt"];
    GlobTestHarness {}.run_test("*.txt".to_string(), false, false, expected);
  }

  #[test]
  fn test_hidden_pattern() {
    assert!(HIDDEN_FILE.is_match("/.test.txt"));
    assert!(HIDDEN_FILE.is_match("/.hidden/test.txt"));
    assert!(HIDDEN_FILE.is_match("/some-dir/.hidden/test.txt"));
    assert!(HIDDEN_FILE.is_match("/not-hidden/.test.txt"));
    assert!(!HIDDEN_FILE.is_match("some-dir/not-hidden/test.txt"));
  }
}
