use crate::common::map_err;
use async_openai::config::OpenAIConfig;
use async_openai::types::{
  ChatCompletionRequestMessage, ChatCompletionRequestUserMessageArgs, ChatCompletionRequestUserMessageContent,
  CreateChatCompletionRequestArgs,
};
use async_openai::Client;
use lazy_static::lazy_static;
use pyo3::pymethods;
use pyo3::types::{PyModule, PyString};
use pyo3::{pyclass, PyResult, Python};
use tokio::runtime::Runtime;

/// Python wrapper for OpenAI Client
#[pyclass(module="bodhilibrs")]
struct OpenAI {
  client: Client<OpenAIConfig>,
}

lazy_static! {
  static ref TOKIO_RUNTIME: Runtime = Runtime::new().unwrap();
}

#[pymethods]
impl OpenAI {
  #[new]
  pub fn init(api_key: &PyString, api_base: Option<&PyString>) -> PyResult<Self> {
    let api_key: String = api_key.extract()?;
    let mut config = OpenAIConfig::default().with_api_key(api_key);
    if let Some(api_base) = api_base {
      let api_base: String = api_base.extract()?;
      config = config.with_api_base(api_base);
    }
    let client = Client::with_config(config);
    Ok(Self { client })
  }

  pub fn generate(&self, _py: Python<'_>, model: &PyString, prompt: &PyString) -> PyResult<Vec<String>> {
    let messages = ChatCompletionRequestUserMessageArgs::default()
      .content(ChatCompletionRequestUserMessageContent::Text(prompt.extract::<String>()?))
      .build()
      .map_err(map_err)?;
    let request =
      CreateChatCompletionRequestArgs::default()
        .messages(vec![ChatCompletionRequestMessage::User(messages)])
        .model(model.extract::<String>()?)
        .build()
        .map_err(map_err)?;
    let chat = self.client.chat();
    let response = TOKIO_RUNTIME.block_on(chat.create(request)).map_err(map_err)?;
    let messages: Vec<String> = response.choices.into_iter().filter_map(|c| c.message.content).collect();
    Ok(messages)
  }
}

pub(crate) fn add_to_module(m: &PyModule) -> PyResult<()> {
  m.add_class::<OpenAI>()?;
  Ok(())
}

#[cfg(test)]
mod test {
  use super::OpenAI;
  use crate::assert_ok;
  use pyo3::{types::PyString, Python};
  use std::env;

  #[test]
  pub fn test_generate() {
    dotenv::from_filename(".env.test").ok().unwrap();
    let api_key = env::var("OPENAI_API_KEY").ok().unwrap();
    Python::with_gil(|py| {
      let api_key = PyString::new(py, &api_key);
      let openai = OpenAI::init(api_key, None);
      assert_ok!(openai);
      let openai = openai.unwrap();
      let model = PyString::new(py, "gpt-3.5-turbo");
      let prompt = PyString::new(py, "What day comes after Monday?");
      let messages = openai.generate(py, model, prompt);
      assert_ok!(messages);
      let messages = messages.unwrap();
      assert_eq!(messages.len(), 1);
      assert!(messages[0].contains("Tuesday"));
    })
  }
}
