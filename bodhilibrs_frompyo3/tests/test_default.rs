mod utils;

use frompyo3::FromPyO3;
use utils::objects::convert_from_code;

#[derive(FromPyO3, Debug, PartialEq)]
struct TestNoDefaultNoOption {
  recursive: bool,
}

#[derive(FromPyO3, Debug, PartialEq)]
struct TestDefaultNoOption {
  #[frompyo3(default = false)]
  recursive: bool,
}

#[derive(FromPyO3, Debug, PartialEq)]
struct TestDefaultOption {
  #[frompyo3(default = false)]
  recursive: Option<bool>,
}

#[derive(FromPyO3, Debug, PartialEq)]
struct TestNoDefaultOption {
  recursive: Option<bool>,
}

const CODE_NO_ATTR: &str = r#"
class TestResource: ...

ret = TestResource()
"#;

const CODE_ATTR_NONE: &str = r#"
class TestResource:
  def __init__(self):
    self.recursive = None

ret = TestResource()
"#;

const CODE_ATTR_TRUE: &str = r#"
class TestResource:
  def __init__(self):
    self.recursive = True

ret = TestResource()
"#;

const CODE_ATTR_FALSE: &str = r#"
class TestResource:
  def __init__(self):
    self.recursive = False

ret = TestResource()
"#;

#[test]
fn test_default_no_default_no_option_raises_err_if_attr_not_present() {
  let obj = convert_from_code::<TestNoDefaultNoOption, _>(CODE_NO_ATTR);
  assert!(obj.is_err());
  let err = obj.unwrap_err();
  assert!(err.contains("object has no attribute 'recursive'"));
}

#[test]
fn test_default_no_default_no_option_raises_err_if_attr_is_none() {
  let obj = convert_from_code::<TestNoDefaultNoOption, _>(CODE_ATTR_NONE);
  assert!(obj.is_err());
  let err = obj.unwrap_err();
  assert!(err.contains("'NoneType' object cannot be converted"));
}

#[test]
fn test_default_no_default_no_option_sets_to_passed_value() {
  let obj = convert_from_code::<TestNoDefaultNoOption, _>(CODE_ATTR_FALSE);
  assert!(obj.is_ok());
  assert_eq!(obj.unwrap(), TestNoDefaultNoOption { recursive: false });
}

#[test]
fn test_default_default_no_option_sets_to_default_value_on_missing_attr() {
  let obj = convert_from_code::<TestDefaultNoOption, _>(CODE_NO_ATTR);
  assert!(obj.is_ok());
  assert_eq!(obj.unwrap(), TestDefaultNoOption { recursive: false });
}

#[test]
fn test_default_default_no_option_sets_to_default_value_on_attr_none() {
  let obj = convert_from_code::<TestDefaultNoOption, _>(CODE_ATTR_NONE);
  assert!(obj.is_ok());
  assert_eq!(obj.unwrap(), TestDefaultNoOption { recursive: false });
}

#[test]
fn test_default_default_no_option_sets_to_passed_value_same_as_default() {
  let obj = convert_from_code::<TestDefaultNoOption, _>(CODE_ATTR_FALSE);
  assert!(obj.is_ok());
  assert_eq!(obj.unwrap(), TestDefaultNoOption { recursive: false });
}

#[test]
fn test_default_default_no_option_sets_to_passed_value_diff_from_default() {
  let obj = convert_from_code::<TestDefaultNoOption, _>(CODE_ATTR_TRUE);
  assert!(obj.is_ok());
  assert_eq!(obj.unwrap(), TestDefaultNoOption { recursive: true });
}

#[test]
fn test_default_default_option_sets_to_default_value_on_no_attr() {
  let obj = convert_from_code::<TestDefaultOption, _>(CODE_NO_ATTR);
  assert!(obj.is_ok());
  assert_eq!(obj.unwrap(), TestDefaultOption { recursive: Some(false) });
}

#[test]
fn test_default_default_option_sets_to_default_value_on_none() {
  let obj = convert_from_code::<TestDefaultOption, _>(CODE_ATTR_NONE);
  assert!(obj.is_ok());
  assert_eq!(obj.unwrap(), TestDefaultOption { recursive: Some(false) });
}

#[test]
fn test_default_default_option_sets_to_passed_value_diff_from_default() {
  let obj = convert_from_code::<TestDefaultOption, _>(CODE_ATTR_TRUE);
  assert!(obj.is_ok());
  assert_eq!(obj.unwrap(), TestDefaultOption { recursive: Some(true) });
}

#[test]
fn test_default_default_option_sets_to_passed_value_same_as_default() {
  let obj = convert_from_code::<TestDefaultOption, _>(CODE_ATTR_FALSE);
  assert!(obj.is_ok());
  assert_eq!(obj.unwrap(), TestDefaultOption { recursive: Some(false) });
}

#[test]
fn test_default_no_default_option_sets_to_none_if_attr_not_present() {
  let obj = convert_from_code::<TestNoDefaultOption, _>(CODE_NO_ATTR);
  assert!(obj.is_ok());
  assert_eq!(obj.unwrap(), TestNoDefaultOption { recursive: None });
}

#[test]
fn test_default_no_default_option_sets_to_none_if_attr_is_none() {
  let obj = convert_from_code::<TestNoDefaultOption, _>(CODE_ATTR_NONE);
  assert!(obj.is_ok());
  assert_eq!(obj.unwrap(), TestNoDefaultOption { recursive: None });
}

#[test]
fn test_default_no_default_option_sets_to_passed_value() {
  let obj = convert_from_code::<TestNoDefaultOption, _>(CODE_ATTR_TRUE);
  assert!(obj.is_ok());
  assert_eq!(obj.unwrap(), TestNoDefaultOption { recursive: Some(true) });
}
