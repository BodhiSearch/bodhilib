use crate::arr_repr;
use crate::async_iter::AsyncListIterator;
use crate::glob;
use pyo3::exceptions::PyAttributeError;
use pyo3::prelude::*;
use pyo3::types::PyIterator;
use pyo3::types::PyList;
use pyo3::{exceptions::PyValueError, types::PyDict};
use std::collections::HashMap;
use std::path::PathBuf;

#[derive(Clone)]
#[pyclass]
struct Resource {
  #[pyo3(get)]
  resource_type: String,
  #[pyo3(get)]
  metadata: HashMap<String, String>,
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

#[pyclass]
struct GlobProcessor {
  #[pyo3(get)]
  pub supported_types: Vec<String>,
  #[pyo3(get)]
  pub service_name: String,
}

impl GlobProcessor {
  arr_repr!(supported_types);
}

#[pymethods]
impl GlobProcessor {
  #[new]
  fn new() -> Self {
    GlobProcessor {
      supported_types: vec!["glob".to_string()],
      service_name: "glob".to_string(),
    }
  }

  fn aprocess<'a>(&self, py: Python<'a>, resource: &PyAny, astream: Option<bool>) -> PyResult<&'a PyAny> {
    let resource_type = resource.getattr("resource_type")?;
    let resource_type = resource_type.extract::<String>()?;
    if resource_type != "glob" {
      let msg =
        format!(
          "Unsupported resource type: {}, supports {}",
          resource_type,
          self.supported_types()
        );
      return Err(PyValueError::new_err(msg));
    }
    let metadata = resource
      .getattr("metadata")
      .map_err(|e| PyValueError::new_err(format!("Failed to get metadata: {}", e)))?;
    let metadata = metadata
      .downcast::<PyDict>()
      .map_err(|e| PyValueError::new_err(format!("Failed to convert metadata to dict: {}", e)))?;
    let path = metadata
      .get_item("path")?
      .ok_or(PyValueError::new_err("Resource metadata does not contain key: 'path'"))?;
    if path.is_none() {
      return Err(PyValueError::new_err("Resource metadata key value is None: 'path'"));
    }
    // check if PosixPath then convert to String
    let path = path.extract::<String>()?;
    let path = PathBuf::from(path);
    if !path.exists() {
      return Err(PyValueError::new_err(format!("Directory does not exist: {}", path.to_str().unwrap())));
    }
    if !path.is_dir() {
      return Err(PyValueError::new_err(format!("Path is not a directory: {}", path.to_str().unwrap())));
    }
    let path = path.canonicalize()?;
    let pattern = metadata
      .get_item("pattern")?
      .ok_or(PyValueError::new_err("Resource metadata does not contain key: 'pattern'"))?;
    if pattern.is_none() {
      return Err(PyValueError::new_err("Resource metadata key value is None: 'pattern'"));
    }
    let pattern = pattern.extract::<String>()?;
    let recursive = metadata.get_item("recursive")?;
    let recursive = match recursive {
      Some(recursive) => recursive.extract::<bool>()?,
      None => false,
    };
    let exclude_hidden = metadata.get_item("exclude_hidden")?;
    let exclude_hidden = match exclude_hidden {
      Some(exclude_hidden) => exclude_hidden.extract::<bool>()?,
      None => false,
    };
    let astream = astream.unwrap_or(false); // TODO: implement astream
    let future = pyo3_asyncio::tokio::future_into_py(py, async move {
      Python::with_gil(|py| {
        let files = glob::glob(&path, &pattern, recursive, !exclude_hidden)
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

  fn process<'a>(&self, resource: &'a PyAny, stream: Option<bool>) -> PyResult<&'a PyAny> {
    let resource_type = resource.getattr("resource_type")?;
    let resource_type = resource_type.extract::<String>()?;
    if resource_type != "glob" {
      let msg =
        format!(
          "Unsupported resource type: {}, supports {}",
          resource_type,
          self.supported_types()
        );
      return Err(PyValueError::new_err(msg));
    }
    let metadata = resource
      .getattr("metadata")
      .map_err(|e| PyValueError::new_err(format!("Failed to get metadata: {}", e)))?;
    let metadata = metadata
      .downcast::<PyDict>()
      .map_err(|e| PyValueError::new_err(format!("Failed to convert metadata to dict: {}", e)))?;
    let path = metadata
      .get_item("path")?
      .ok_or(PyValueError::new_err("Resource metadata does not contain key: 'path'"))?;
    if path.is_none() {
      return Err(PyValueError::new_err("Resource metadata key value is None: 'path'"));
    }
    // check if PosixPath then convert to String
    let path = path.extract::<String>()?;
    let path = PathBuf::from(path);
    if !path.exists() {
      return Err(PyValueError::new_err(format!("Directory does not exist: {}", path.to_str().unwrap())));
    }
    if !path.is_dir() {
      return Err(PyValueError::new_err(format!("Path is not a directory: {}", path.to_str().unwrap())));
    }
    let path = path.canonicalize()?;
    let pattern = metadata
      .get_item("pattern")?
      .ok_or(PyValueError::new_err("Resource metadata does not contain key: 'pattern'"))?;
    if pattern.is_none() {
      return Err(PyValueError::new_err("Resource metadata key value is None: 'pattern'"));
    }
    let pattern = pattern.extract::<String>()?;
    let recursive = metadata.get_item("recursive")?;
    let recursive = match recursive {
      Some(recursive) => recursive.extract::<bool>()?,
      None => false,
    };
    let exclude_hidden = metadata.get_item("exclude_hidden")?;
    let exclude_hidden = match exclude_hidden {
      Some(exclude_hidden) => exclude_hidden.extract::<bool>()?,
      None => false,
    };
    let stream = stream.unwrap_or(false); // TODO: implement stream
    let files = glob::glob(&path, &pattern, recursive, !exclude_hidden).unwrap();
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
      result.append(resource.into_py(py)).unwrap();
    });
    if stream {
      Ok(PyIterator::from_object(result)?)
    } else {
      Ok(result)
    }
  }

  fn __repr__(&self) -> String {
    format!(
      "GlobProcessor(service_name={}, supported_types=['{}'])",
      self.service_name,
      self.supported_types.join("', '")
    )
  }
}

pub(crate) fn add_to_module(m: &PyModule) -> PyResult<()> {
  m.add_class::<GlobProcessor>()?;
  m.add_class::<Resource>()?;
  Ok(())
}
