mod models;
use models::*;
use pm2::Ident;
use proc_macro2 as pm2;
use proc_macro2::TokenStream;
use quote::quote;
use syn::parse_macro_input;
use syn::{spanned::Spanned, DeriveInput, FieldsNamed};

const FROMPYO3: &str = "frompyo3";
type Result<T> = std::result::Result<T, E>;

#[proc_macro_derive(FromPyO3, attributes(frompyo3))]
pub fn derive_from_py_o3(input: proc_macro::TokenStream) -> proc_macro::TokenStream {
  let ast = parse_macro_input!(input as DeriveInput);
  let gen = parse_data(&ast);
  let result = match gen {
    Ok(result) => result,
    Err(err) => match err {
      E::One(err) => err.into_compile_error(),
      E::Many(errs) => {
        let errs = errs.into_iter().map(|err| err.into_compile_error()).collect::<Vec<_>>();
        quote! {
          #(#errs)*
        }
      }
    },
  };
  result.into()
}

fn parse_data(ast: &DeriveInput) -> Result<TokenStream> {
  let struct_meta: StructMeta = parse_struct_meta(ast)?;
  let field_metas: Vec<FieldMeta> = parse_field_meta(ast)?;
  parse_named_fields(&struct_meta, &field_metas)
}

fn parse_struct_meta(ast: &DeriveInput) -> Result<StructMeta> {
  let mut struct_attrs = ast
    .attrs
    .clone()
    .into_iter()
    .filter(|a| a.path().is_ident(FROMPYO3))
    .collect::<Vec<_>>();
  let struct_attr = match struct_attrs.len() {
    0 => Ok(StructAttr { name: None }),
    1 => {
      let struct_attr = struct_attrs.pop().expect("should have element at index 0");
      struct_attr.parse_args::<StructAttr>().map_err(E::One)
    }
    len if len > 1 => Err(E::Many(
      ast
        .attrs
        .clone()
        .into_iter()
        .map(|a| syn::Error::new(a.span(), "Multiple attributes not supported"))
        .collect::<Vec<_>>(),
    )),
    len => {
      unreachable!("len cannot be less than 0: {}", len)
    }
  }?;
  Ok(StructMeta {
    ident: IdentWrapper(ast.ident.clone()),
    struct_attr,
  })
}

fn parse_field_meta(ast: &DeriveInput) -> Result<Vec<FieldMeta>> {
  let span = ast.span();
  match &ast.data {
    syn::Data::Struct(data) => match &data.fields {
      syn::Fields::Named(fields_named) => {
        let field_attrs = parse_field_attrs(fields_named);
        let (oks, errs): (Vec<_>, Vec<_>) = field_attrs.into_iter().partition(|result| result.is_ok());
        if !errs.is_empty() {
          let errs = errs.into_iter().map(|r| r.unwrap_err()).collect::<Vec<_>>();
          let errs: E = errs
            .into_iter()
            .fold(Vec::new(), |mut acc, err| {
              match err {
                E::One(err) => acc.push(err),
                E::Many(mut errs) => acc.append(&mut errs),
              }
              acc
            })
            .into();
          Err(errs)
        } else {
          let field_metas = oks
            .into_iter()
            .map(|ok| ok.expect("should not have any errors"))
            .collect::<Vec<_>>();
          Ok(field_metas)
        }
      }
      syn::Fields::Unnamed(e) => Err(syn::Error::new(e.span(), "Unnamed fields are not supported").into()),
      syn::Fields::Unit => Err(syn::Error::new(data.fields.span(), "Unit structs are not supported").into()),
    },
    syn::Data::Enum(_) => Err(syn::Error::new(span, "Enums are not supported").into()),
    syn::Data::Union(_) => Err(syn::Error::new(span, "Unions are not supported").into()),
  }
}

fn parse_field_attrs(fields_named: &FieldsNamed) -> Vec<Result<FieldMeta>> {
  let field_attrs =
    fields_named
      .named
      .clone()
      .into_iter()
      .map(|f| {
        let mut field_attrs = f
          .attrs
          .clone()
          .into_iter()
          .filter(|a| a.path().is_ident(FROMPYO3))
          .collect::<Vec<_>>();
        match field_attrs.len() {
          len if len > 1 => {
            let errs = field_attrs
              .iter()
              .map(|f| syn::Error::new(f.span(), "Multiple attributes not supported"))
              .collect::<Vec<_>>();
            Err(E::Many(errs))
          }
          1 => {
            let field_attr = field_attrs.pop().unwrap();
            match field_attr.parse_args::<FieldAttr>() {
              Ok(field_attr) => {
                let field_meta = FieldMeta {
                  ident: f.ident.clone().expect("field ident should be present").into(),
                  ty: f.ty.clone(),
                  field_attr,
                };
                Ok(field_meta)
              }
              Err(err) => Err(E::One(err)),
            }
          }
          0 => Ok(FieldMeta {
            ident: f.ident.clone().expect("field ident should be present").into(),
            ty: f.ty.clone(),
            field_attr: FieldAttr {
              dict: None,
              default: None,
            },
          }),
          len => unreachable!("len is less than 0: {}", len),
        }
      })
      .collect::<Vec<_>>();
  field_attrs
}

fn parse_named_fields(struct_meta: &StructMeta, field_metas: &[FieldMeta]) -> Result<TokenStream> {
  let common_methods = parse_common_methods(field_metas)?;
  let extractions = field_metas
    .iter()
    .map(|f| parse_named_field(f, struct_meta))
    .collect::<Vec<_>>();
  let (oks, errs): (Vec<_>, Vec<_>) = extractions.into_iter().partition(|r| r.is_ok());
  if !errs.is_empty() {
    let errs: Vec<syn::Error> = errs.into_iter().fold(Vec::new(), |mut acc, err| {
      match err.unwrap_err() {
        E::One(err) => acc.push(err),
        E::Many(mut errs) => acc.append(&mut errs),
      };
      acc
    });
    return Err(E::Many(errs));
  }
  let extractions = oks
    .into_iter()
    .map(|ok| ok.expect("should not be error"))
    .collect::<Vec<_>>();
  let field_names = field_metas.iter().map(|f| &f.ident.0).collect::<Vec<_>>();
  let name = &struct_meta.ident.0;
  let result = quote! {
    impl std::convert::TryFrom<&pyo3::types::PyAny> for #name {
      type Error = pyo3::PyErr;
      fn try_from(value: &pyo3::types::PyAny) -> pyo3::PyResult<Self> {
          #common_methods
          #( #extractions )*
          Ok(Self { #( #field_names ),* })
      }
    }
  };
  Ok(result)
}

fn parse_common_methods(field_metas: &[FieldMeta]) -> Result<TokenStream> {
  let gens = field_metas
    .iter()
    .filter(|f| f.field_attr.dict.is_some())
    .map(|f| {
      let dict_name = f.field_attr.dict.as_ref().expect("should be present");
      let dict_id = Ident::new(dict_name, f.ident.0.span());
      quote! {
        let #dict_id = value.getattr(#dict_name)
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("Failed to get value from attribute: {}", #dict_name)))?
        .downcast::<pyo3::types::PyDict>()
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(
          format!("Failed to convert {} to dict: {}", #dict_name, e)))?;
      }
    })
    .collect::<Vec<_>>();
  Ok(quote! {
    #(#gens)*
  })
}

fn parse_named_field(field_meta: &FieldMeta, struct_meta: &StructMeta) -> Result<TokenStream> {
  match &field_meta.field_attr.dict {
    Some(_) => extract_from_dict(field_meta, struct_meta),
    None => extract_field(field_meta),
  }
}

fn extract_field(field_meta: &FieldMeta) -> Result<TokenStream> {
  let name = &field_meta.ident.0;
  let name_str = name.to_string();
  let ty = &field_meta.ty;
  let result = if field_meta.is_option() || field_meta.field_attr.default.as_ref().is_some() {
    let default_value = field_meta.default_value()?;
    quote! {
      let #name = match value.getattr(#name_str) {
        Ok(#name) => { if #name.is_none() {
            Ok(#default_value)
          } else {
            Ok(#name.extract::<#ty>()?)
          }
        },
        Err(e) => { if e.is_instance_of::<pyo3::exceptions::PyAttributeError>(value.py()) {
            Ok(#default_value)
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

fn extract_from_dict(field_meta: &FieldMeta, struct_meta: &StructMeta) -> Result<TokenStream> {
  let resource_name = struct_meta
    .struct_attr
    .name
    .as_ref()
    .map(|name| name.to_string())
    .unwrap_or_else(|| struct_meta.ident.0.to_string());
  let field_ident = &field_meta.ident.0;
  let field_name = field_ident.to_string();
  let ty = &field_meta.ty;
  let dict_name = field_meta.field_attr.dict.as_ref().expect("dict should be present");
  let dict_id = Ident::new(dict_name, field_ident.span());

  let result = if field_meta.is_option() || field_meta.has_default() {
    let default_value = field_meta.default_value()?;
    quote! {
      let #field_ident = match #dict_id.get_item(#field_name)? {
        Some(#field_ident) if !#field_ident.is_none() => #field_ident.extract::<#ty>()?,
        Some(#field_ident) => #default_value,
        None => #default_value,
      };
    }
  } else {
    quote! {
      let #field_ident = #dict_id.get_item(#field_name)?
          .ok_or(pyo3::exceptions::PyValueError::new_err(
              format!("{} {} does not contain key: '{}'", #resource_name, #dict_name, #field_name)))?;
      if #field_ident.is_none() {
          return Err(pyo3::exceptions::PyValueError::new_err(format!("{}['{}'] is None", #resource_name, #field_name)));
      }
      let #field_ident = #field_ident.extract::<#ty>()?;
    }
  };
  Ok(result)
}
