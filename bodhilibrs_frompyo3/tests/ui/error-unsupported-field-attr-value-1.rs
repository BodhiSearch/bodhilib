use frompyo3::FromPyO3;

#[derive(FromPyO3)]
struct TestUnsupportedFieldAttrMultiple {
  #[frompyo3(dict = metadata)]
  path: String,
}

fn main() {}
