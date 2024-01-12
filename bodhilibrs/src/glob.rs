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

pub fn glob(path: &Path, pattern: &str, recursive: bool, hidden: bool) -> Result<Vec<String>, GlobError> {
  let options = g::MatchOptions {
    case_sensitive: true,
    require_literal_separator: !recursive,
    require_literal_leading_dot: !hidden,
  };
  let mut paths = Vec::<String>::new();
  let mut path = path.to_path_buf();
  if recursive {
    path = path.join("**");
  }
  let glob_pattern = path.join(pattern);
  let glob_pattern = glob_pattern.to_str().ok_or_else(|| GlobError {
    message: "pattern not provided".to_string(),
  })?;
  for entry in g::glob_with(glob_pattern, options).map_err(|e| GlobError { message: e.to_string() })? {
    match entry {
      Ok(path) => {
        if path.is_dir() {
          continue;
        }
        if let Some(path) = path.to_str() {
          // macos have tmp dir in symbolic `/private` folder
          let path = path.trim_start_matches("/private");
          paths.push(path.to_string());
        }
      }
      Err(_) => continue,
    }
  }
  Ok(paths)
}

#[cfg(test)]
mod test {
  use super::glob;
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
    let mut files = glob(temp_dir, "*.txt", true, true).unwrap();
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
    let mut files = glob(temp_dir, "*.txt", true, false).unwrap();
    assert_eq!(files.len(), 2);
    files.sort();
    assert_eq!(files[0], build_path(temp_dir, "test1.txt"));
    assert_eq!(files[1], build_path(temp_dir, "tmpdir2/test4.txt"));
  }

  #[test]
  pub fn test_glob_no_recursive_hidden() {
    let setup = Setup::new();
    let temp_dir = setup.path();
    let mut files = glob(temp_dir, "*.txt", false, true).unwrap();
    assert_eq!(files.len(), 2);
    files.sort();
    assert_eq!(files[0], build_path(temp_dir, ".test3.txt"));
    assert_eq!(files[1], build_path(temp_dir, "test1.txt"));
  }

  #[test]
  pub fn test_glob_no_recursive_no_hidden() {
    let setup = Setup::new();
    let temp_dir = setup.path();
    let mut files = glob(temp_dir, "*.txt", false, false).unwrap();
    assert_eq!(files.len(), 1);
    files.sort();
    assert_eq!(files[0], build_path(temp_dir, "test1.txt"));
  }

  fn build_path(tmpdir: &Path, file: &str) -> String {
    let file = PathBuf::from(tmpdir).to_path_buf().join(file).canonicalize().unwrap();
    let file0 = file.to_str().expect("failed to join path");
    let file0 = file0.trim_start_matches("/private");
    file0.to_string()
  }
}
