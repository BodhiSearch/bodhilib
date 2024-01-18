use crate::_glob;
use crate::_glob::GlobResult;
use crate::async_iter::AsyncGenIterator;
use crate::async_iter::GenIterator;
use crate::common::Resource;
use frompyo3::FromPyO3;
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
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
      let result = _glob::glob(&path, &input.pattern, input.recursive, !input.exclude_hidden, astream)
        .map_err(|e| PyValueError::new_err(format!("{}", e)))?;
      match result {
        GlobResult::Iter(paths) => Ok(AsyncGenIterator { paths }.into_py(py)),
        GlobResult::List(paths) => {
          let resources = PyList::empty(py);
          paths.into_iter().for_each(|file| {
            let mut metadata = HashMap::new();
            metadata.insert("path".to_string(), file);
            metadata.insert("resource_type".to_string(), "local_file".to_string());
            let resource = Resource {
              resource_type: "local_file".to_string(),
              metadata,
            };
            resources.append(resource.into_py(py)).unwrap();
          });
          let result: Py<PyAny> = resources.into_py(py);
          Ok(result)
        }
      }
    })
  });
  future
}

#[pyfunction]
fn glob_sync(resource: &PyAny, stream: Option<bool>) -> PyResult<&PyAny> {
  let input = GlobInput::try_from(resource)?;
  let stream = stream.unwrap_or(false);
  let path = PathBuf::from(&input.path).canonicalize()?;
  let glob_result = _glob::glob(&path, &input.pattern, input.recursive, !&input.exclude_hidden, stream)
    .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("Error: {}", e)))?;
  let py = resource.py();
  match glob_result {
    GlobResult::Iter(paths) => {
      let iter = GenIterator { paths }.into_py(py);
      Ok(iter.into_ref(py))
    }
    GlobResult::List(files) => {
      let result = PyList::empty(py);
      files.into_iter().for_each(|file| {
        let resource = to_resource(py, file);
        result.append(resource).unwrap();
      });
      Ok(result)
    }
  }
}

fn to_resource(py: Python, file: String) -> Py<PyAny> {
  let mut metadata = HashMap::new();
  metadata.insert("path".to_string(), file);
  metadata.insert("resource_type".to_string(), "local_file".to_string());
  Resource {
    resource_type: "local_file".to_string(),
    metadata,
  }
  .into_py(py)
}

pub(crate) fn add_to_module(m: &PyModule) -> PyResult<()> {
  m.add_function(wrap_pyfunction!(glob_sync, m)?)?;
  m.add_function(wrap_pyfunction!(glob_async, m)?)?;
  Ok(())
}
