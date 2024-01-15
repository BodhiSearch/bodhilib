use syn::parse::{Parse, ParseStream};
use syn::{Expr, Ident, LitStr, Token, Type};

#[derive(Debug)]
pub(crate) enum E {
  One(syn::Error),
  Many(Vec<syn::Error>),
}

impl From<syn::Error> for E {
  fn from(val: syn::Error) -> Self {
    E::One(val)
  }
}

impl From<Vec<syn::Error>> for E {
  fn from(val: Vec<syn::Error>) -> Self {
    E::Many(val)
  }
}

#[derive(Debug)]
pub(crate) struct IdentWrapper(pub Ident);

impl From<Ident> for IdentWrapper {
  fn from(value: Ident) -> Self {
    IdentWrapper(value)
  }
}

#[derive(Debug)]
pub(crate) struct StructAttr {
  pub name: Option<String>,
}

#[derive(Debug)]
pub(crate) struct StructMeta {
  pub ident: IdentWrapper,
  pub struct_attr: StructAttr,
}

impl Parse for StructAttr {
  fn parse(input: ParseStream) -> syn::Result<Self> {
    let mut name = None;
    while !input.is_empty() {
      if input.peek(Token![,]) {
        input.parse::<Token![,]>()?;
        continue;
      }
      let attr_name: Ident = input.parse()?;
      input.parse::<Token![=]>()?;
      if attr_name == "name" {
        let attr_value: LitStr = input.parse()?;
        name = Some(attr_value.value());
      } else {
        return Err(syn::Error::new(
          attr_name.span(),
          format!("Unsupported struct attribute key: '{}'", attr_name),
        ));
      }
      if input.peek(Token![,]) {
        input.parse::<Token![,]>()?;
      }
    }
    Ok(StructAttr { name })
  }
}

#[derive(Debug)]
pub(crate) struct FieldMeta {
  pub ident: IdentWrapper,
  pub ty: Type,
  pub field_attr: FieldAttr,
}

impl FieldMeta {
  pub(crate) fn is_option(&self) -> bool {
    match &self.ty {
      Type::Path(path) => {
        let segments = &path.path.segments;
        if let Some(first_segment) = segments.first() {
          first_segment.ident == "Option"
        } else {
          false
        }
      }
      _ => false,
    }
  }
}

#[derive(Debug)]
pub(crate) struct FieldAttr {
  pub dict: Option<String>,
  pub default: Option<syn::Expr>,
}

impl Parse for FieldAttr {
  fn parse(input: ParseStream) -> syn::Result<Self> {
    let mut dict = None;
    let mut default = None;
    while !input.is_empty() {
      if input.peek(Token![,]) {
        input.parse::<Token![,]>()?;
        continue;
      }
      let attr_name: Ident = input.parse()?;
      let attr_name_str = attr_name.to_string();
      input.parse::<Token![=]>()?;
      match attr_name_str {
        _ if attr_name_str == "dict" => {
          dict = Some(input.parse::<LitStr>()?.value());
        }
        _ if attr_name_str == "default" => {
          default = Some(input.parse::<Expr>()?);
        }
        attr_name_str => {
          return Err(syn::Error::new(
            attr_name.span(),
            format!("Unsupported field level attribute: '{}'", attr_name_str),
          ))
        }
      }
      if input.peek(Token![,]) {
        input.parse::<Token![,]>()?;
      }
    }
    Ok(FieldAttr { dict, default })
  }
}
