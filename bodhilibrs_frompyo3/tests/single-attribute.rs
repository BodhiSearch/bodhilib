use frompyo3::FromPyO3;

#[derive(FromPyO3, Debug, PartialEq)]
pub(crate) struct GlobResource {
  pub(crate) resource_type: String,
}

#[test]
fn test_single_attribute() {
  use pyo3::{types::PyDict, Python};
  Python::with_gil(|py| {
    let locals = PyDict::new(py);
    py.run(
      r#"
class TestResource:
  def __init__(self):
    self.resource_type = "glob"
ret = TestResource()
"#,
      None,
      Some(locals),
    )
    .expect("should create test object");
    let result = locals
      .get_item("ret")
      .expect("should build test object")
      .expect("should build test object");
    let test_obj = GlobResource::try_from(result).expect("should convert to GlobResource");
    assert_eq!(
      test_obj,
      GlobResource {
        resource_type: "glob".to_string()
      }
    );
  });
}

fn main() {}
