use frompyo3::FromPyO3;

#[derive(FromPyO3)]
struct TestUnsupportedFieldAttrMultiple {
  #[frompyo3(dict = "metadata")]
  #[frompyo3(foo = "bar")]
  #[frompyo3(baz = "caz")]
  path: String,
}

fn main() {}
