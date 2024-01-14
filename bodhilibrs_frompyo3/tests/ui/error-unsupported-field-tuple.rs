use frompyo3::FromPyO3;

#[derive(FromPyO3)]
struct TestUnsupportedFieldTuple(i32, i32);

fn main() {}
