use pyo3::exceptions::PyStopAsyncIteration;
use pyo3::prelude::*;
use pyo3::types::PyList;
use pyo3_asyncio::tokio::future_into_py;

#[pyclass]
pub(crate) struct AsyncListIterator {
  list: Py<PyList>,
  current: usize,
}

impl AsyncListIterator {
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

pub(crate) fn add_to_module(m: &PyModule) -> PyResult<()> {
  m.add_class::<AsyncListIterator>()?;
  Ok(())
}
