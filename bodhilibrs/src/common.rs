use async_openai::error::OpenAIError;
use pyo3::create_exception;
use pyo3::types::PyModule;
use pyo3::{PyErr, PyResult};

create_exception!(bodhilibrs, BodhilibException, pyo3::exceptions::PyException);

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
  m.add("BodhilibException", py.get_type::<BodhilibException>())?;
  Ok(())
}
