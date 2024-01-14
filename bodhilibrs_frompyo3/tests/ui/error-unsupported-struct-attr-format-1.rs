use frompyo3::FromPyO3;

#[derive(FromPyO3)]
#[frompyo3(name)]
struct TestUnsupportedStructAttr {}

fn main() {}
