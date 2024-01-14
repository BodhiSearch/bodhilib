use frompyo3::FromPyO3;

#[derive(FromPyO3)]
#[frompyo3( = "Resource")]
struct TestUnsupportedStructAttr {}

fn main() {}
