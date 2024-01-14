use frompyo3::FromPyO3;

#[derive(FromPyO3)]
#[frompyo3(unknown = "Resource")]
struct TestUnsupportedStructKey {}

fn main() {}
