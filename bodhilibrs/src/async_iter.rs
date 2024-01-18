use std::collections::HashMap;

use pyo3::exceptions::PyStopAsyncIteration;
use pyo3::prelude::*;
use pyo3::types::PyList;
use pyo3_asyncio::tokio::future_into_py;

use crate::common::Resource;

#[pyclass]
pub(crate) struct AsyncListIterator {
  list: Py<PyList>,
  current: usize,
}

impl AsyncListIterator {
  #[allow(unused)]
  pub(crate) fn new(list: Py<PyList>) -> Self {
    AsyncListIterator { list, current: 0 }
  }
}

#[pymethods]
impl AsyncListIterator {
  #[new]
  fn __new__(list: Py<PyList>) -> Self {
    AsyncListIterator { list, current: 0 }
  }

  fn __anext__(slf: Py<Self>, py: Python) -> PyResult<Option<PyObject>> {
    let list_clone = slf.borrow(py).list.clone();
    let fut = async move {
      Python::with_gil(move |py| {
        let mut slf = slf.borrow_mut(py);
        let list = list_clone.as_ref(py);
        if slf.current < list.len() {
          let current = list.get_item(slf.current)?;
          slf.current += 1;
          Ok(current.into_py(py))
        } else {
          Err(PyStopAsyncIteration::new_err("StopAsyncIteration"))
        }
      })
    };
    let future = future_into_py(py, fut)?;
    Ok(Some(future.into()))
  }

  fn __aiter__(slf: Py<Self>) -> Py<Self> {
    slf
  }
}

#[pyclass]
pub struct AsyncGenIterator {
  pub paths: glob::Paths,
}

#[pymethods]
impl AsyncGenIterator {
  fn __anext__(slf: Py<Self>, py: Python) -> PyResult<Option<PyObject>> {
    let fut =
      async move {
        Python::with_gil(|py| {
          let result = loop {
            let result = slf.borrow_mut(py).paths.next();
            match result {
              Some(Ok(path)) => {
                let path = path.to_str().unwrap();
                let resource = to_resource(path);
                break Some(resource);
              }
              Some(Err(_)) => continue,
              None => break None,
            }
          };
          match result {
            Some(resource) => Ok(resource.into_py(py)),
            None => Err(PyStopAsyncIteration::new_err("StopAsyncIteration")),
          }
        })
      };
    let future: &PyAny = future_into_py(py, fut)?;
    Ok(Some(future.into()))
  }

  fn __aiter__(slf: Py<Self>) -> Py<Self> {
    slf
  }
}

#[pyclass]
pub struct GenIterator {
  pub paths: glob::Paths,
}

#[pymethods]
impl GenIterator {
  fn __next__(slf: Py<Self>, py: Python) -> Option<Py<PyAny>> {
    loop {
      let result = slf.borrow_mut(py).paths.next();
      match result {
        Some(Ok(path)) => {
          let path = path.to_str().unwrap();
          let resource = to_resource(path);
          let resource_py = resource.into_py(py);
          return Some(resource_py);
        }
        Some(Err(_)) => continue,
        None => return None,
      }
    }
  }

  fn __iter__(slf: Py<Self>) -> Py<Self> {
    slf
  }
}

fn to_resource(file: &str) -> Resource {
  let mut metadata = HashMap::new();
  metadata.insert("path".to_string(), file.trim_start_matches("/private").to_string());
  metadata.insert("resource_type".to_string(), "local_file".to_string());
  Resource {
    resource_type: "local_file".to_string(),
    metadata,
  }
}

pub(crate) fn add_to_module(m: &PyModule) -> PyResult<()> {
  m.add_class::<AsyncListIterator>()?;
  m.add_class::<AsyncGenIterator>()?;
  m.add_class::<GenIterator>()?;
  Ok(())
}
