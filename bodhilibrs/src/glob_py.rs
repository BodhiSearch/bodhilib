use crate::async_iter::AsyncListIterator;
use crate::common::Resource;
use crate::glob;
use frompyo3::FromPyO3;
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyIterator;
use pyo3::types::PyList;
use std::collections::HashMap;
use std::path::PathBuf;

#[pyclass]
struct GlobProcessor {}

#[derive(FromPyO3)]
struct GlobInput {
  path: String,
  pattern: String,
  recursive: bool,
  exclude_hidden: bool,
}

#[pyfunction]
fn glob_async<'a>(py: Python<'a>, resource: &PyAny, astream: Option<bool>) -> PyResult<&'a PyAny> {
  let input = GlobInput::try_from(resource)?;
  let astream = astream.unwrap_or(false);
  let path = PathBuf::from(&input.path).canonicalize()?;
  let future = pyo3_asyncio::tokio::future_into_py(py, async move {
    Python::with_gil(|py| {
      let files = glob::glob(&path, &input.pattern, input.recursive, !input.exclude_hidden)
        .map_err(|e| PyValueError::new_err(format!("{}", e)))?;
      let resources = PyList::empty(py);
      files.into_iter().for_each(|file| {
        let mut metadata = HashMap::new();
        metadata.insert("path".to_string(), file);
        metadata.insert("resource_type".to_string(), "local_file".to_string());
        let resource = Resource {
          resource_type: "local_file".to_string(),
          metadata,
        };
        resources.append(resource.into_py(py)).unwrap();
      });
      let result: Py<PyAny> = if astream {
        AsyncListIterator::new(resources.into_py(py)).into_py(py)
      } else {
        resources.into_py(py)
      };
      Ok(result)
    })
  });
  future
}

#[pyfunction]
fn glob_sync(resource: &PyAny, stream: Option<bool>) -> PyResult<&PyAny> {
  let input = GlobInput::try_from(resource)?;
  let stream = stream.unwrap_or(false);
  let path = PathBuf::from(&input.path).canonicalize()?;
  let files = glob::glob(&path, &input.pattern, input.recursive, !&input.exclude_hidden).unwrap();
  let py = resource.py();
  let result = PyList::empty(py);
  files.into_iter().for_each(|file| {
    let mut metadata = HashMap::new();
    metadata.insert("path".to_string(), file);
    metadata.insert("resource_type".to_string(), "local_file".to_string());
    let resource = Resource {
      resource_type: "local_file".to_string(),
      metadata,
    }
    .into_py(py);
    result.append(resource).unwrap();
  });
  if stream {
    Ok(PyIterator::from_object(result)?)
  } else {
    Ok(result)
  }
}

pub(crate) fn add_to_module(m: &PyModule) -> PyResult<()> {
  m.add_function(wrap_pyfunction!(glob_sync, m)?)?;
  m.add_function(wrap_pyfunction!(glob_async, m)?)?;
  Ok(())
}
