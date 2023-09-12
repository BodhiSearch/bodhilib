bodhilib
========

.. automodule:: bodhilib
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __iter__

.. data:: PromptInput

   Type alias for various inputs that can be passed to the LLM service as prompt.

   Defined as Union[:class:`str`, List[str], :class:`~bodhilib.models.Prompt`, List[:class:`~bodhilib.models.Prompt`], Dict[str, Any], List[Dict[str, Any]]]

   LLM service can take in::
      - a string, the string value is treated as prompt "text", role is set to "user" and source is set to "input"
      - a list of strings, builds prompt with same defaults as above
      - a :class:`~bodhilib.models.Prompt` object
      - a list of :class:`~bodhilib.models.Prompt` objects
      - a serialized :class:`~bodhilib.models.Prompt` object as dict, e.g. `{"text": "hello", "role": "user", "source": "input"}`
      - a list of serialized :class:`~bodhilib.models.Prompt` objects as dicts

.. autodata:: bodhilib._data_loader.T

.. autodata:: bodhilib._embedder.T

.. autodata:: bodhilib._llm.T