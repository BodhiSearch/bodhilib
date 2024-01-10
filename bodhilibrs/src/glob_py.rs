use std::collections::HashMap;
use std::path::PathBuf;

use crate::arr_repr;
use crate::glob;
use pyo3::exceptions::PyAttributeError;
use pyo3::{exceptions::PyValueError, prelude::*, types::PyDict};

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

  fn process(&self, resource: &PyAny) -> PyResult<Vec<Resource>> {
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
    let files = glob::glob(&path, &pattern, recursive, !exclude_hidden).unwrap();
    let files = files
      .into_iter()
      .map(|file| {
        let mut metadata = HashMap::new();
        metadata.insert("path".to_string(), file);
        metadata.insert("resource_type".to_string(), "local_file".to_string());
        Resource {
          resource_type: "local_file".to_string(),
          metadata,
        }
      })
      .collect::<Vec<Resource>>();
    Ok(files)
  }
}

pub(crate) fn add_to_module(m: &PyModule) -> PyResult<()> {
  m.add_class::<GlobProcessor>()?;
  Ok(())
}
