use std::{fmt::Display, path::Path};

use glob as g;

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
    let entry = process_entry(entry);
    if let Some(path) = entry {
      result.push(path);
    }
  }
  Ok(GlobResult::List(result))
}

pub struct GlobIterator {
  pub paths: glob::Paths,
}

impl Iterator for GlobIterator {
  type Item = String;

  fn next(&mut self) -> Option<Self::Item> {
    loop {
      let entry = self.paths.next();
      match entry {
        Some(entry) => {
          let entry = process_entry(entry);
          if let Some(entry) = entry {
            return Some(entry);
          }
        }
        None => return None,
      }
    }
  }
}

fn process_entry(entry: Result<std::path::PathBuf, g::GlobError>) -> Option<String> {
  match entry {
    Ok(path) => {
      if path.is_dir() {
        return None;
      }
      if let Some(path) = path.to_str() {
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
  use super::{glob, GlobIterator, GlobResult};
  use std::fs::File;
  use std::io::Write;
  use std::path::{Path, PathBuf};

  struct Setup {
    temp_dir: tempfile::TempDir,
  }

  impl Setup {
    fn new() -> Self {
      let temp_dir = tempfile::tempdir().expect("failed to create temp dir");
      let files = vec!["test1.txt", "test2.csv", ".test3.txt"];
      for file in files {
        let mut file = File::create(temp_dir.path().join(file)).expect("failed to create tempfile");
        writeln!(file, "hello world").unwrap();
      }
      // create a new directory inside temp_dir
      let subdir = temp_dir.path().join("tmpdir2");
      std::fs::create_dir(&subdir).expect("failed to create subdir");
      let files = vec!["test4.txt", ".test5.txt"];
      for file in files {
        let mut file = File::create(subdir.join(file)).expect("failed to create tempfile");
        writeln!(file, "hello world").unwrap();
      }
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
    let mut files = extract_files(result);
    assert_eq!(files.len(), 4);
    files.sort();
    assert_eq!(files[0], build_path(temp_dir, ".test3.txt"));
    assert_eq!(files[1], build_path(temp_dir, "test1.txt"));
    assert_eq!(files[2], build_path(temp_dir, "tmpdir2/.test5.txt"));
    assert_eq!(files[3], build_path(temp_dir, "tmpdir2/test4.txt"));
  }

  #[test]
  pub fn test_glob_recursive_no_hidden() {
    let setup = Setup::new();
    let temp_dir = setup.path();
    let result = glob(temp_dir, "*.txt", true, false, false).unwrap();
    let mut files = extract_files(result);
    assert_eq!(files.len(), 2);
    files.sort();
    assert_eq!(files[0], build_path(temp_dir, "test1.txt"));
    assert_eq!(files[1], build_path(temp_dir, "tmpdir2/test4.txt"));
  }

  #[test]
  pub fn test_glob_no_recursive_hidden() {
    let setup = Setup::new();
    let temp_dir = setup.path();
    let result = glob(temp_dir, "*.txt", false, true, false).unwrap();
    let mut files = extract_files(result);
    assert_eq!(files.len(), 2);
    files.sort();
    assert_eq!(files[0], build_path(temp_dir, ".test3.txt"));
    assert_eq!(files[1], build_path(temp_dir, "test1.txt"));
  }

  #[test]
  pub fn test_glob_no_recursive_no_hidden() {
    let setup = Setup::new();
    let temp_dir = setup.path();
    let result = glob(temp_dir, "*.txt", false, false, false).unwrap();
    let mut files = extract_files(result);
    assert_eq!(files.len(), 1);
    files.sort();
    assert_eq!(files[0], build_path(temp_dir, "test1.txt"));
  }

  #[test]
  fn test_glob_stream() {
    let setup = Setup::new();
    let temp_dir = setup.path();
    let result = glob(temp_dir, "*.txt", true, true, true).unwrap();
    let paths = extract_paths(result);
    let mut files: Vec<String> = GlobIterator { paths }.collect();
    assert_eq!(files.len(), 4);
    files.sort();
    assert_eq!(files[0], build_path(temp_dir, ".test3.txt"));
    assert_eq!(files[1], build_path(temp_dir, "test1.txt"));
    assert_eq!(files[2], build_path(temp_dir, "tmpdir2/.test5.txt"));
    assert_eq!(files[3], build_path(temp_dir, "tmpdir2/test4.txt"));
  }

  fn build_path(tmpdir: &Path, file: &str) -> String {
    let file = PathBuf::from(tmpdir).to_path_buf().join(file).canonicalize().unwrap();
    let file0 = file.to_str().expect("failed to join path");
    let file0 = file0.trim_start_matches("/private");
    file0.to_string()
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
