bodhilib
========

.. data:: bodhilib.PathLike

   Type alias for Union of :class:`str` and :class:`pathlib.Path`

.. data:: bodhilib.TextLike

   Type alias for Union of :class:`str` and protocol :data:`~bodhilib.SupportsText`

.. data:: bodhilib.TextLikeOrTextLikeList

   Type alias for Union of :data:`~bodhilib.TextLike` and :class:`~typing.List`\[:data:`~bodhilib.TextLike`\]

.. data:: bodhilib.PromptInput

   Type alias for various inputs that can be passed to the LLM service as prompt.

   Defined as Union[:class:`str`, List[str], :class:`~bodhilib.Prompt`, List[:class:`~bodhilib.Prompt`], Dict[str, Any], List[Dict[str, Any]]]

   LLM service can take in::
      - a string, the string value is treated as prompt "text", role is set to "user" and source is set to "input"
      - a list of strings, builds prompt with same defaults as above
      - a :class:`~bodhilib.Prompt` object
      - a list of :class:`~bodhilib.Prompt` objects
      - a serialized :class:`~bodhilib.Prompt` object as dict, e.g. `{"text": "hello", "role": "user", "source": "input"}`
      - a list of serialized :class:`~bodhilib.Prompt` objects as dicts

.. data:: bodhilib.Embedding

   Type alias for `List[float]`, to indicate the embedding generated from :class:`~bodhilib.Embedder` operation.

.. automodule:: bodhilib
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __iter__
   :private-members: _embed, _split, _StrEnumMixin

.. data:: bodhilib.C

   TypeVar for bodhilib Components

.. data:: bodhilib.T

   TypeVar for LLM API response
   
.. data:: bodhilib.DL

   TypeVar for type bound to :class:`~bodhilib.DataLoader`

.. data:: bodhilib.E

   TypeVar for type bound to :class:`~bodhilib.Embedder`

.. data:: bodhilib.L

   TypeVar for type bound to :class:`~bodhilib.LLM`

.. data:: bodhilib.V

   TypeVar for type bound to :class:`~bodhilib.VectorDB`

.. class:: bodhilib._models._StrEnumMixin

   Mixin class to support string enums
