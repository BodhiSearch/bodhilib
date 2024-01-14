use frompyo3::FromPyO3;

#[derive(FromPyO3)]
struct TestUnsupportedUnit(i32);

fn main() {}
