use frompyo3::FromPyO3;

#[derive(FromPyO3)]
#[frompyo3(name = "Resource")]
#[frompyo3(foo = "bar")]
#[frompyo3(baz = "caz")]
struct TestUnsupportedStructAttrMultiple {
  path: String,
}

fn main() {}
