use frompyo3::FromPyO3;

#[derive(FromPyO3)]
#[frompyo3(name = "foo")]
#[frompyo3(name = "bar")]
struct TestMultipleStructAttrs {}

fn main() {}
