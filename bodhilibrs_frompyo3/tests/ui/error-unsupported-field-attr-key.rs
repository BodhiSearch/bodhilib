use frompyo3::FromPyO3;

#[derive(FromPyO3)]
struct TestUnsupportedFieldAttrKey {
  #[frompyo3(unknown = "metadata")]
  path: String,
}

fn main() {}
