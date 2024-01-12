use frompyo3::FromPyO3;

#[derive(FromPyO3)]
pub(crate) struct GlobResource {
  #[frompyo3(dict = "metadata")]
  path: String,
  #[frompyo3(dict = "metadata")]
  recursive: bool,
}
