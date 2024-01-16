use pyo3::prelude::*;
use pyo3::types::{PyAny, PyDict};
use std::convert::TryFrom;
use std::fmt::Debug;

pub(crate) fn convert_from_code<T, E>(code: &str) -> Result<T, String>
where
  T: for<'py> TryFrom<&'py PyAny, Error = E>,
  E: Debug,
{
  Python::with_gil(|py| -> Result<T, String> {
    let locals = PyDict::new(py);
    py.run(code, None, Some(locals)).expect("Failed to run python code");

    let py_any = locals
      .get_item("ret")
      .expect("Item 'ret' not found in locals")
      .expect("unwrap");

    T::try_from(py_any).map_err(|e| format!("Failed to convert from &PyAny: {:?}", e))
  })
}
