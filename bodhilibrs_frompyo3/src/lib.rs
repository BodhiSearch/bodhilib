use std::collections::HashSet;

use pm2::Ident;
use proc_macro::TokenStream;
use proc_macro2 as pm2;
use quote::quote;
use quote::quote_spanned;
use syn::parse_macro_input;
use syn::{
  spanned::Spanned,
  Attribute,
  Data::Struct,
  DataStruct, DeriveInput, Expr, Field,
  Fields::{Named, Unit, Unnamed},
  FieldsNamed, Lit, Meta,
  Type::Path,
};

#[proc_macro_derive(FromPyO3, attributes(frompyo3))]
pub fn derive_from_py_o3(input: TokenStream) -> TokenStream {
  let ast = parse_macro_input!(input as DeriveInput);
  let gen = parse_data(&ast);
  let result = match gen {
    Ok(ts) => ts,
    Err(ts) => ts,
  };
  result.into()
}

fn parse_data(ast: &DeriveInput) -> Result<pm2::TokenStream, pm2::TokenStream> {
  let name = &ast.ident;
  let span = ast.span();
  match &ast.data {
    Struct(data) => parse_struct(name, data),
    _ => Err(quote_spanned!(span => compile_error!("FromPyO3 is only defined for structs"))),
  }
}

fn parse_struct(name: &pm2::Ident, struct_: &DataStruct) -> Result<pm2::TokenStream, pm2::TokenStream> {
  match &struct_.fields {
    Named(fields) => parse_named_fields(name, fields),
    Unnamed(_) => panic!("FromPyO3 is only defined for named fields"),
    Unit => panic!("FromPyO3 is only defined for named fields"),
  }
}

fn parse_named_fields(name: &pm2::Ident, fields: &FieldsNamed) -> Result<pm2::TokenStream, pm2::TokenStream> {
  let common_methods = parse_common_methods(fields)?;
  let extractions = fields.named.iter().map(parse_named_field).collect::<Vec<_>>();
  let mut errors = extractions
    .clone()
    .into_iter()
    .filter(|e| e.is_err())
    .collect::<Vec<_>>();
  if !errors.is_empty() {
    return errors.pop().unwrap();
  }
  let extractions = extractions.into_iter().map(|e| e.unwrap()).collect::<Vec<_>>();
  let field_name = &fields.named.iter().map(|f| &f.ident).collect::<Vec<_>>();
  let result = quote! {
    impl std::convert::TryFrom<&pyo3::types::PyAny> for #name {
      type Error = pyo3::PyErr;

      fn try_from(value: &pyo3::types::PyAny) -> pyo3::PyResult<Self> {
          #( #common_methods )*
          #( #extractions )*
          Ok(Self { #( #field_name ),* })
      }
    }
  };
  Ok(result)
}

fn parse_common_methods(fields: &FieldsNamed) -> Result<Vec<pm2::TokenStream>, pm2::TokenStream> {
  let dicts = fields
    .named
    .iter()
    .map(|f| extract_field_attrs(&f.attrs))
    .collect::<Vec<_>>();
  let err = dicts.clone().into_iter().find(|r| r.is_err());
  if let Some(err) = err {
    return Err(err.unwrap_err());
  }
  let dicts = dicts.into_iter().filter_map(|r| r.unwrap()).collect::<HashSet<_>>();
  let result = dicts.into_iter().map(|dict_name| {
    let dict_id = Ident::new(&dict_name, pm2::Span::call_site());
    quote! {
      let #dict_id = value.getattr(#dict_name)
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Failed to get value from attribute: {}", #dict_name)))?
        .downcast::<pyo3::types::PyDict>()
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(
          format!("Failed to convert {} to dict: {}", #dict_name, e)))?;
    }
  }).collect::<Vec<_>>();
  Ok(result)
}

fn parse_named_field(f: &Field) -> Result<pm2::TokenStream, pm2::TokenStream> {
  let attr = extract_field_attrs(&f.attrs)?;
  match attr {
    Some(dict_name) => extract_from_dict(f, &dict_name),
    None => extract_field(f),
  }
}

fn extract_field(f: &Field) -> Result<pm2::TokenStream, pm2::TokenStream> {
  let span = f.span();
  let name = f
    .ident
    .as_ref()
    .ok_or_else(|| quote_spanned!(span => compile_error!("Field identifier is missing")))?;
  let name_str = name.to_string();
  let ty = &f.ty;
  let result =
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
    };
  Ok(result)
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

fn extract_from_dict(f: &Field, dict_name: &str) -> Result<pm2::TokenStream, pm2::TokenStream> {
  let span = f.span();
  let name = f
    .ident
    .as_ref()
    .ok_or_else(|| quote_spanned!(span => compile_error!("Field ident is missing")))?;
  let name_str = name.to_string();
  let ty = &f.ty;
  let dict_id = Ident::new(dict_name, pm2::Span::call_site());
  let result = if is_option(f) {
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
  };
  Ok(result)
}

fn extract_field_attrs(attrs: &[Attribute]) -> Result<Option<String>, pm2::TokenStream> {
  if attrs.is_empty() {
    return Ok(None);
  }
  if attrs.len() > 1 {
    let span = attrs.get(1).unwrap().span();
    return Err(quote_spanned!(span => compile_error!("Multiple field attributes not supported")));
  }
  let attr = attrs.first().unwrap();
  let parsed_attr = attr.parse_args::<Meta>();
  let span = attr.span();
  match parsed_attr {
    Ok(parsed_attr) => match parsed_attr {
      Meta::NameValue(pair) => {
        if !pair.path.is_ident("dict") {
          Err(quote_spanned!(span => compile_error!("Unsupported field level attribute")))
        } else {
          match &pair.value {
            Expr::Lit(lit) => match &lit.lit {
              Lit::Str(lit) => Ok(Some(lit.value())),
              _ => Err(quote_spanned!(span => compile_error!("Unsupported field attribute value format"))),
            },
            _ => Err(quote_spanned!(span => compile_error!("Unsupported field attribute value format"))),
          }
        }
      }
      _ => Err(quote_spanned!(span => compile_error!("Unsupported field level attribute format"))),
    },
    Err(_) => Err(quote_spanned!(span => compile_error!("Failed to parse field attribute"))),
  }
}
