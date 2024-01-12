use frompyo3::FromPyO3;

#[derive(FromPyO3, Debug, PartialEq)]
pub(crate) struct GlobResource {
  resource_type: String,
  recursive: Option<bool>,
}

const CODE_OPTIONAL_ABSENT: &str = r#"
class TestResource:
  def __init__(self):
    self.resource_type = "glob"

resource = TestResource()
"#;
const CODE_OPTIONAL_PRESENT: &str = r#"
class TestResource:
  def __init__(self):
    self.resource_type = "glob"
    self.recursive = False

resource = TestResource()
"#;

#[test]
fn test_optional_absent() {
  use pyo3::{types::PyDict, Python};
  Python::with_gil(|py| {
    let locals = PyDict::new(py);
    py.run(CODE_OPTIONAL_ABSENT, None, Some(locals))
      .expect("should create test object");
    let resource = locals
      .get_item("resource")
      .expect("should have created test object")
      .expect("should have created test object");
    let resource = GlobResource::try_from(resource).expect("should have converted to Rust type");
    assert_eq!(
      resource,
      GlobResource {
        resource_type: "glob".to_string(),
        recursive: None,
      }
    );
  });
}

#[test]
fn test_optional_present() {
  use pyo3::{types::PyDict, Python};
  Python::with_gil(|py| {
    let locals = PyDict::new(py);
    py.run(CODE_OPTIONAL_PRESENT, None, Some(locals))
      .expect("should create test object");
    let resource = locals
      .get_item("resource")
      .expect("should have created test object")
      .expect("should have created test object");
    let resource = GlobResource::try_from(resource).expect("should have converted to Rust type");
    assert_eq!(
      resource,
      GlobResource {
        resource_type: "glob".to_string(),
        recursive: Some(false),
      }
    );
  });
}

fn main() {}
