mod common;
mod glob;
mod glob_py;
mod openai_py;
use pyo3::prelude::*;

/// A Python module implemented in Rust.
#[pymodule]
fn bodhilibrs(_py: Python, m: &PyModule) -> PyResult<()> {
  common::add_to_module(m)?;
  glob_py::add_to_module(m)?;
  openai_py::add_to_module(m)?;
  Ok(())
}

#[macro_export]
macro_rules! assert_ok {
  ($e:expr) => {
    match &$e {
      Ok(_) => (),
      Err(e) => {
        assert!(false, "Expected Ok, got Err: {:?}", e);
      }
    }
  };
}

#[macro_export]
macro_rules! arr_repr {
  ($arr:ident) => {
    fn $arr(&self) -> String {
      let quoted = self
        .$arr
        .iter()
        .map(|s| format!("'{}'", s))
        .collect::<Vec<_>>()
        .join(", ");
      format!("[{}]", quoted)
    }
  };
}
