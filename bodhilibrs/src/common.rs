use std::collections::HashMap;

use async_openai::error::OpenAIError;
use pyo3::create_exception;
use pyo3::exceptions::PyAttributeError;
use pyo3::prelude::*;
use pyo3::types::PyModule;
use pyo3::{PyErr, PyResult};
create_exception!(bodhilibrs, BodhilibException, pyo3::exceptions::PyException);

#[derive(Clone)]
#[pyclass]
pub(crate) struct Resource {
  #[pyo3(get)]
  pub(crate) resource_type: String,
  #[pyo3(get)]
  pub(crate) metadata: HashMap<String, String>,
}

#[pymethods]
impl Resource {
  fn __getattr__(&self, name: String) -> PyResult<String> {
    let value = self.metadata.get(&name);
    match value {
      Some(value) => Ok(value.to_string()),
      None => Err(PyAttributeError::new_err(format!("'Resource' object has no attribute '{}'", name))),
    }
  }
  fn __repr__(&self) -> PyResult<String> {
    let path = self.metadata.get("path").unwrap();
    Ok(format!("Resource(resource_type='{}', path='{}')", self.resource_type, path))
  }
}

pub struct BodhilibError {
  reason: String,
}

impl From<BodhilibError> for PyErr {
  fn from(value: BodhilibError) -> Self {
    PyErr::new::<BodhilibException, _>(value.reason)
  }
}

impl From<OpenAIError> for BodhilibError {
  fn from(value: OpenAIError) -> Self {
    let reason = match value {
      OpenAIError::Reqwest(e) => format!("IOException: {}", e),
      OpenAIError::ApiError(e) => format!("APIError: {}", e.message),
      OpenAIError::JSONDeserialize(_) => todo!(),
      OpenAIError::FileSaveError(_) => todo!(),
      OpenAIError::FileReadError(_) => todo!(),
      OpenAIError::StreamError(_) => todo!(),
      OpenAIError::InvalidArgument(e) => format!("InvalidArgs: {}", e),
    };
    Self { reason }
  }
}

pub(crate) fn map_err(e: OpenAIError) -> PyErr {
  BodhilibError::from(e).into()
}

pub(crate) fn add_to_module(m: &PyModule) -> PyResult<()> {
  let py = m.py();
  m.add_class::<Resource>()?;
  m.add("BodhilibException", py.get_type::<BodhilibException>())?;
  Ok(())
}
