use rayon::prelude::*;
use regex::Regex;
use std::{collections::VecDeque, fs, io::Read};

#[derive(Debug, Clone)]
pub struct RecursiveCharacterTextSplitter {
  pub separators: Vec<String>,
  pub keep_separator: bool,
  pub is_separator_regex: bool,
  pub _strip_whitespace: bool,
  pub _chunk_size: usize,
  pub _chunk_overlap: usize,
}

impl RecursiveCharacterTextSplitter {
  pub fn new(
    separators: Option<Vec<String>>,
    keep_separator: bool,
    is_separator_regex: bool,
    chunk_size: usize,
    chunk_overlap: usize,
    strip_whitespace: bool,
  ) -> Self {
    RecursiveCharacterTextSplitter {
      separators: separators.unwrap_or_else(|| vec!["\n\n".into(), "\n".into(), " ".into(), "".into()]),
      keep_separator,
      is_separator_regex,
      _chunk_size: chunk_size,
      _chunk_overlap: chunk_overlap,
      _strip_whitespace: strip_whitespace,
    }
  }

  pub fn split_text(&self, text: &str, separators: Vec<String>) -> Vec<String> {
    let mut final_chunks = Vec::new();
    let mut separator = separators.last().unwrap().clone();
    let mut new_separators = Vec::new();

    for (i, sep) in separators.iter().enumerate() {
      let _separator = if self.is_separator_regex {
        sep.clone()
      } else {
        regex::escape(sep)
      };
      if sep.is_empty() {
        separator = sep.clone();
        break;
      }
      if Regex::new(&_separator).unwrap().is_match(text) {
        separator = sep.clone();
        new_separators = separators[i + 1..].to_vec();
        break;
      }
    }

    let _separator = if self.is_separator_regex {
      separator.clone()
    } else {
      regex::escape(&separator)
    };
    let splits = self.split_text_with_regex(text, &_separator, self.keep_separator);

    let mut good_splits = VecDeque::new();
    let separator_for_merge = if self.keep_separator {
      "".to_string()
    } else {
      separator.clone()
    };

    for s in splits {
      if s.len() < self._chunk_size {
        good_splits.push_back(s);
      } else {
        if !good_splits.is_empty() {
          let merged_text = self.merge_splits(&mut good_splits, &separator_for_merge);
          final_chunks.extend(merged_text);
        }
        if new_separators.is_empty() {
          final_chunks.push(s);
        } else {
          let other_info = self.split_text(&s, new_separators.clone());
          final_chunks.extend(other_info);
        }
      }
    }

    if !good_splits.is_empty() {
      let merged_text = self.merge_splits(&mut good_splits, &separator_for_merge);
      final_chunks.extend(merged_text);
    }

    final_chunks
  }

  fn merge_splits(&self, splits: &mut VecDeque<String>, separator: &str) -> Vec<String> {
    let separator_len = separator.len();
    let mut docs: Vec<String> = Vec::new();
    let mut current_doc: Vec<String> = Vec::new();
    let mut total = 0;

    for d in splits.drain(..) {
      let len = d.len();
      if total + len + if !current_doc.is_empty() { separator_len } else { 0 } > self._chunk_size {
        if total > self._chunk_size {
          eprintln!(
            "Created a chunk of size {}, which is longer than the specified {}",
            total, self._chunk_size
          );
        }
        if !current_doc.is_empty() {
          if let Some(doc) = self.join_docs(&current_doc, separator) {
            docs.push(doc);
          }
          while total > self._chunk_overlap
            || (total + len + if !current_doc.is_empty() { separator_len } else { 0 } > self._chunk_size && total > 0)
          {
            total -= current_doc[0].len() + if current_doc.len() > 1 { separator_len } else { 0 };
            current_doc.remove(0);
          }
        }
      }
      current_doc.push(d);
      total += len + if current_doc.len() > 1 { separator_len } else { 0 };
    }
    if let Some(doc) = self.join_docs(&current_doc, separator) {
      docs.push(doc);
    }

    docs
  }

  fn split_text_with_regex(&self, text: &str, separator: &str, keep_separator: bool) -> Vec<String> {
    let mut splits = Vec::new();

    if !separator.is_empty() {
      let regex = Regex::new(separator).unwrap();
      if keep_separator {
        let mut last = 0;
        for mat in regex.find_iter(text) {
          splits.push(text[last..mat.start()].to_string());
          splits.push(mat.as_str().to_string());
          last = mat.end();
        }
        splits.push(text[last..].to_string());
      } else {
        splits = regex.split(text).map(String::from).collect();
      }
    } else {
      splits = text.chars().map(|c| c.to_string()).collect();
    }
    splits.into_iter().filter(|s| !s.is_empty()).collect()
  }

  fn join_docs(&self, docs: &[String], separator: &str) -> Option<String> {
    let mut text = docs.join(separator);
    if self._strip_whitespace {
      text = text.trim().to_string();
    }
    if text.is_empty() {
      None
    } else {
      Some(text)
    }
  }

  pub fn split_files(&self, files: Vec<std::path::PathBuf>) -> Vec<(String, Vec<String>)> {
    files
      .par_iter()
      .map(|path| {
        let mut contents = String::new();
        let mut file = fs::File::open(path).unwrap();
        let _ = file.read_to_string(&mut contents).unwrap();
        let filename = path.file_name().unwrap().to_str().unwrap().to_string();
        (filename, self.split_text(&contents, self.separators.clone()))
      })
      .collect::<Vec<_>>()
  }
}

#[cfg(test)]
mod test {
  use std::fs;

  use super::RecursiveCharacterTextSplitter;
  #[test]
  pub fn test_splitter() {
    let separators = vec!["\n\n".into(), "\n".into(), " ".into(), "".into()];
    let splitter = RecursiveCharacterTextSplitter {
      separators: separators.clone(),
      keep_separator: true,
      is_separator_regex: false,
      _strip_whitespace: true,
      _chunk_size: 100,
      _chunk_overlap: 20,
    };
    // read the file to string
    let text = fs::read_to_string("tests/data/pg_superlinear.md").unwrap();
    let result = splitter.split_text(&text, separators.clone());
    assert_eq!(result.len(), 343);
  }
}
