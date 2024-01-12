use std::collections::HashSet;

use pm2::Ident;
use proc_macro::TokenStream;
use proc_macro2 as pm2;
use quote::quote;
use syn::{
  parse_macro_input, Attribute,
  Data::{Enum, Struct, Union},
  DataStruct, DeriveInput, Expr, Field,
  Fields::{Named, Unit, Unnamed},
  FieldsNamed, Lit, Meta, MetaNameValue,
  Type::Path,
};

#[derive(Debug, PartialEq)]
struct FromPyO3FieldAttr {
  dict_name: Option<String>,
}

#[proc_macro_derive(FromPyO3, attributes(frompyo3))]
pub fn derive_from_py_o3(input: TokenStream) -> TokenStream {
  let ast = parse_macro_input!(input as DeriveInput);
  let gen = parse_data(&ast);
  gen.into()
}

fn parse_data(ast: &DeriveInput) -> proc_macro2::TokenStream {
  let name = &ast.ident;
  match &ast.data {
    Struct(data) => parse_struct(name, data),
    Enum(_) => panic!("FromPyO3 is only defined for structs"),
    Union(_) => panic!("FromPyO3 is only defined for structs"),
  }
}

fn parse_struct(name: &pm2::Ident, struct_: &DataStruct) -> proc_macro2::TokenStream {
  match &struct_.fields {
    Named(fields) => parse_named_fields(name, fields),
    Unnamed(_) => panic!("FromPyO3 is only defined for named fields"),
    Unit => panic!("FromPyO3 is only defined for named fields"),
  }
}

fn parse_named_fields(name: &pm2::Ident, fields: &FieldsNamed) -> proc_macro2::TokenStream {
  let common_methods = parse_common_methods(fields);
  let extractions = &fields.named.iter().map(parse_named_field).collect::<Vec<_>>();
  let field_name = &fields.named.iter().map(|f| &f.ident).collect::<Vec<_>>();
  quote! {
    impl std::convert::TryFrom<&pyo3::types::PyAny> for #name {
      type Error = pyo3::PyErr;

      fn try_from(value: &pyo3::types::PyAny) -> pyo3::PyResult<Self> {
          #( #common_methods )*
          #( #extractions )*
          Ok(Self { #( #field_name ),* })
      }
    }
  }
}

fn parse_common_methods(fields: &FieldsNamed) -> Vec<pm2::TokenStream> {
  let mut dicts = HashSet::new();
  for field in &fields.named {
    if let FromPyO3FieldAttr {
      dict_name: Some(dict_name),
      ..
    } = extract_attrs(&field.attrs)
    {
      dicts.insert(dict_name);
    }
  }
  dicts.into_iter().map(|dict_name| {
    let dict_id = Ident::new(&dict_name, pm2::Span::call_site());
    quote! {
      let #dict_id = value.getattr(#dict_name)
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Failed to get value from attribute: {}", #dict_name)))?
        .downcast::<pyo3::types::PyDict>()
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(
          format!("Failed to convert {} to dict: {}", #dict_name, e)))?;
    }
  }).collect::<Vec<_>>()
}

fn parse_named_field(f: &Field) -> pm2::TokenStream {
  let attr = extract_attrs(&f.attrs);
  match &attr.dict_name {
    Some(dict_name) => extract_from_dict(f, dict_name),
    None => extract_field(f),
  }
}

fn extract_field(f: &Field) -> pm2::TokenStream {
  let name = f.ident.as_ref().expect("field name is not specified");
  let name_str = name.to_string();
  let ty = &f.ty;
  if is_option(f) {
    quote! {
      let #name = match value.getattr(#name_str) {
        Ok(#name) => {
          if #name.is_none() {
            Ok(None)
          } else {
            Ok(#name.extract::<#ty>()?)
          }
        },
        Err(e) => {
          if e.is_instance_of::<pyo3::exceptions::PyAttributeError>(value.py()) {
            Ok(None)
          } else {
            Err(e)
          }
        },
      }?;
    }
  } else {
    quote! {
      let #name = value.getattr(#name_str)?.extract::<#ty>()?;
    }
  }
}

fn is_option(f: &Field) -> bool {
  if let Path(type_path) = &f.ty {
    let segments = &type_path.path.segments;
    if let Some(first_segment) = segments.first() {
      return first_segment.ident == "Option";
    }
  }
  false
}

fn extract_from_dict(f: &Field, dict_name: &str) -> pm2::TokenStream {
  let name = f.ident.as_ref().expect("field name is not specified");
  let name_str = name.to_string();
  let ty = &f.ty;
  let dict_id = Ident::new(dict_name, pm2::Span::call_site());
  if is_option(f) {
    quote! {
      let #name = match #dict_id.get_item(#name_str)? {
        Some(#name) => #name.extract::<#ty>()?,
        None => None,
      };
    }
  } else {
    quote! {
      let #name = #dict_id.get_item(#name_str)?
          .ok_or(pyo3::exceptions::PyValueError::new_err(
              format!("{} does not contain key: '{}'", #dict_name, #name_str)))?;
      if #name.is_none() {
          return Err(pyo3::exceptions::PyValueError::new_err(format!("{}['{}'] is None", #dict_name, #name_str)));
      }
      let #name = #name.extract::<#ty>()?;
    }
  }
}

fn extract_attrs(attrs: &[Attribute]) -> FromPyO3FieldAttr {
  let mut result = FromPyO3FieldAttr { dict_name: None };
  for attr in attrs {
    let attr = attr
      .parse_args::<Meta>()
      .expect("failed to parse attribute as key-value");
    match &attr {
      Meta::NameValue(pair) => {
        result.dict_name = extract_dict(pair);
      }
      Meta::List(_) => {
        panic!("incorrect format for field attribute, expecting name-value pair, got list")
      }
      Meta::Path(_) => panic!("incorrect format for field attribute, expecting name-value pair, got path"),
    }
  }
  result
}

fn extract_dict(pair: &MetaNameValue) -> Option<String> {
  let dict = pair.path.segments.first()?;
  if dict.ident != "dict" {
    return None;
  }
  match &pair.value {
    Expr::Lit(lit) => match &lit.lit {
      Lit::Str(s) => Some(s.value()),
      e => {
        panic!("incorrect format for field attribute, expecting string, found {:?}", e)
      }
    },
    e => panic!("incorrect format for field attribute, expecting string, found {:?}", e),
  }
}

#[cfg(test)]
mod test {
  use quote::quote;
  use syn::FieldsNamed;

  use crate::FromPyO3FieldAttr;

  #[test]
  pub fn test_extract_field_attributes() {
    let input = quote! {
      {
        #[frompyo3(dict = "metadata")]
        pub(crate) path: String,
      }
    };
    let fields = syn::parse2::<FieldsNamed>(input).expect("should parse as FieldsNamed");
    let path = fields.named.first().expect("should have the path field");
    let field_attr = super::extract_attrs(&path.attrs);
    assert_eq!(
      field_attr,
      FromPyO3FieldAttr {
        dict_name: Some("metadata".to_string())
      }
    );
  }
}
