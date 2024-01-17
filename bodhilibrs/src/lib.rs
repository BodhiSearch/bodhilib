mod async_iter;
mod common;
mod glob;
mod glob_py;
mod openai_py;
use pyo3::prelude::*;

/// A Python module implemented in Rust.
#[pymodule]
fn bodhilibrs(_py: Python, m: &PyModule) -> PyResult<()> {
  async_iter::add_to_module(m)?;
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
