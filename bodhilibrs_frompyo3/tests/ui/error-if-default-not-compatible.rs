use frompyo3::FromPyO3;

#[derive(FromPyO3)]
struct TestDefault {
  #[frompyo3(default = 1)]
  recursive: bool,
}

fn main() {}
