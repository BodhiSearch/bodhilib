use frompyo3::FromPyO3;

#[derive(FromPyO3)]
#[frompyo3(name = Resource)]
struct TestUnsupportedStructValueLiteral {}

fn main() {}
