use frompyo3::FromPyO3;

#[derive(FromPyO3)]
union TestUnsupportedUnion {
  weight: i32,
  temp: f32,
}

fn main() {}
