use glob as g;
use lazy_static::lazy_static;
use regex::Regex;
use std::{fmt::Display, path::Path};

lazy_static! {
  static ref HIDDEN_FILE: Regex = {
    let pattern = format!(r#".*\{}\.\w+.*"#, std::path::MAIN_SEPARATOR);
    Regex::new(&pattern).unwrap()
  };
}

#[derive(Debug)]
pub struct GlobError {
  message: String,
}

impl Display for GlobError {
  fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
    f.write_str(&format!("Error: {}", self.message))
  }
}

pub enum GlobResult {
  Iter(g::Paths),
  List(Vec<String>),
}

pub fn glob(path: &Path, pattern: &str, recursive: bool, hidden: bool, stream: bool) -> Result<GlobResult, GlobError> {
  let options = g::MatchOptions {
    case_sensitive: true,
    require_literal_separator: !recursive,
    require_literal_leading_dot: !hidden,
  };
  let mut path = path.to_path_buf();
  if recursive {
    path = path.join("**");
  }
  let glob_pattern = path.join(pattern);
  let glob_pattern = glob_pattern.to_str().ok_or_else(|| GlobError {
    message: "error building glob pattern".to_string(),
  })?;
  let paths = g::glob_with(glob_pattern, options).map_err(|e| GlobError { message: e.to_string() })?;
  if stream {
    return Ok(GlobResult::Iter(paths));
  }
  let mut result = Vec::<String>::new();
  for entry in paths {
    let entry = process_entry(entry, hidden);
    if let Some(path) = entry {
      result.push(path);
    }
  }
  Ok(GlobResult::List(result))
}

pub struct GlobIterator {
  pub paths: glob::Paths,
  pub hidden: bool,
}

impl Iterator for GlobIterator {
  type Item = String;

  fn next(&mut self) -> Option<Self::Item> {
    loop {
      let entry = self.paths.next();
      match entry {
        Some(entry) => {
          let entry = process_entry(entry, self.hidden);
          if let Some(entry) = entry {
            return Some(entry);
          }
        }
        None => return None,
      }
    }
  }
}

fn process_entry(entry: Result<std::path::PathBuf, g::GlobError>, hidden: bool) -> Option<String> {
  match entry {
    Ok(path) => {
      if path.is_dir() {
        return None;
      }
      if let Some(path) = path.to_str() {
        // split using OS separator and check if any of directory starts with "."
        if !hidden && HIDDEN_FILE.is_match(path) {
          return None;
        }
        // macos have tmp dir in symbolic `/private` folder
        let path = path.trim_start_matches("/private");
        Some(path.to_string())
      } else {
        None
      }
    }
    Err(e) => {
      eprintln!("Error while browsing directory: {}", e);
      None
    }
  }
}

#[cfg(test)]
mod test {
  use super::{glob, GlobIterator, GlobResult, HIDDEN_FILE};
  use std::fs::File;
  use std::io::Write;
  use std::path::Path;

  struct Setup {
    temp_dir: tempfile::TempDir,
  }

  impl Setup {
    fn new() -> Self {
      let temp_dir = tempfile::Builder::new()
        .prefix("glob_test")
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

    fn path(&self) -> &Path {
      self.temp_dir.path()
    }
  }

  #[test]
  pub fn test_glob_recursive_hidden() {
    let setup = Setup::new();
    let temp_dir = setup.path();
    let result = glob(temp_dir, "*.txt", true, true, false).unwrap();
    let files = extract_files(result);
    assert_eq!(files.len(), 6);
    let root_dir = temp_dir.to_str().unwrap();
    let mut files = files
      .into_iter()
      .map(|path| path.trim_start_matches(root_dir).to_owned())
      .collect::<Vec<_>>();
    files.sort();
    let expected = vec![
      "/.test3.txt",
      "/.tmpdir3/.test7.txt",
      "/.tmpdir3/test6.txt",
      "/test1.txt",
      "/tmpdir2/.test5.txt",
      "/tmpdir2/test4.txt",
    ]
    .into_iter()
    .map(|path| path.to_owned())
    .collect::<Vec<_>>();
    assert_eq!(files, expected);
  }

  #[test]
  pub fn test_glob_recursive_no_hidden() {
    let setup = Setup::new();
    let temp_dir = setup.path();
    let root_dir = temp_dir.to_str().unwrap();
    let result = glob(temp_dir, "*.txt", true, false, false).unwrap();
    let mut files = extract_files(result)
      .into_iter()
      .map(|path| path.trim_start_matches(root_dir).to_owned())
      .collect::<Vec<_>>();
    files.sort();
    let expected = vec!["/test1.txt", "/tmpdir2/test4.txt"]
      .into_iter()
      .map(|path| path.to_owned())
      .collect::<Vec<_>>();
    assert_eq!(files, expected);
  }

  #[test]
  pub fn test_glob_no_recursive_hidden() {
    let setup = Setup::new();
    let temp_dir = setup.path();
    let root_dir = temp_dir.to_str().unwrap();
    let result = glob(temp_dir, "*.txt", false, true, false).unwrap();
    let mut files = extract_files(result)
      .into_iter()
      .map(|path| path.trim_start_matches(root_dir).to_owned())
      .collect::<Vec<_>>();
    files.sort();
    let expected = vec!["/.test3.txt", "/test1.txt"]
      .into_iter()
      .map(|path| path.to_owned())
      .collect::<Vec<_>>();
    assert_eq!(files, expected);
  }

  #[test]
  pub fn test_glob_no_recursive_no_hidden() {
    let setup = Setup::new();
    let temp_dir = setup.path();
    let root_dir = temp_dir.to_str().unwrap();
    let result = glob(temp_dir, "*.txt", false, false, false).unwrap();
    let mut files = extract_files(result)
      .into_iter()
      .map(|path| path.trim_start_matches(root_dir).to_owned())
      .collect::<Vec<_>>();
    files.sort();
    let expected = vec!["/test1.txt"]
      .into_iter()
      .map(|path| path.to_owned())
      .collect::<Vec<_>>();
    assert_eq!(files, expected);
  }

  #[test]
  fn test_glob_stream() {
    let setup = Setup::new();
    let temp_dir = setup.path();
    let root_dir = temp_dir.to_str().unwrap();
    let result = glob(temp_dir, "*.txt", true, true, true).unwrap();
    let paths = extract_paths(result);
    let mut files: Vec<String> = GlobIterator { paths, hidden: true }
      .map(|path| path.trim_start_matches(root_dir).to_owned())
      .collect();
    files.sort();
    let expected = vec![
      "/.test3.txt",
      "/.tmpdir3/.test7.txt",
      "/.tmpdir3/test6.txt",
      "/test1.txt",
      "/tmpdir2/.test5.txt",
      "/tmpdir2/test4.txt",
    ];
    assert_eq!(files, expected);
  }

  #[test]
  fn test_hidden_pattern() {
    assert!(HIDDEN_FILE.is_match("/.test.txt"));
    assert!(HIDDEN_FILE.is_match("/.hidden/test.txt"));
    assert!(HIDDEN_FILE.is_match("/some-dir/.hidden/test.txt"));
    assert!(HIDDEN_FILE.is_match("/not-hidden/.test.txt"));
    assert!(!HIDDEN_FILE.is_match("some-dir/not-hidden/test.txt"));
  }

  fn create_files(inside: &Path, files: Vec<&str>) {
    for file in files {
      let mut file = File::create(inside.join(file)).expect("failed to create tempfile");
      writeln!(file, "hello world").unwrap();
    }
  }

  fn extract_files(result: GlobResult) -> Vec<String> {
    if let GlobResult::List(files) = result {
      files
    } else {
      panic!("expected GlobResult to be a ::List")
    }
  }

  fn extract_paths(result: GlobResult) -> glob::Paths {
    if let GlobResult::Iter(paths) = result {
      paths
    } else {
      panic!("expected GlobResult to be a ::Iter")
    }
  }
}
