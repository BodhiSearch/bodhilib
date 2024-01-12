use frompyo3::FromPyO3;

#[derive(FromPyO3, Debug, PartialEq)]
pub(crate) struct GlobResource {
  resource_type: String,
  #[frompyo3(dict = "metadata")]
  pub(crate) path: String,
}

#[test]
fn test_extracts_from_dict() {
  use pyo3::{types::PyDict, Python};
  Python::with_gil(|py| {
    let locals = PyDict::new(py);
    py.run(
      r#"
class TestResource:
  def __init__(self, metadata):
    self.metadata = metadata
    self.resource_type = "glob"

resource = TestResource({"path": "/path/to/resource", "recursive": False})
    "#,
      None,
      Some(locals),
    )
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
        path: "/path/to/resource".to_string(),
      }
    );
  });
}

fn main() {}
