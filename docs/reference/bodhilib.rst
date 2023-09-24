bodhilib
========

.. data:: bodhilib.PathLike

   Type alias for Union of :class:`str` and :class:`pathlib.Path`

.. data:: bodhilib.TextLike

   Type alias for Union of :class:`str` and protocol :data:`~bodhilib.SupportsText`

.. data:: bodhilib.TextLikeOrTextLikeList

   Type alias for Union of :data:`~bodhilib.TextLike` and :class:`~typing.List`\[:data:`~bodhilib.TextLike`\]

.. data:: bodhilib.SerializedInput

   Type alias for a generic and flexible input types that can be passed to the Service components
   like :class:`~bodhilib.LLM`, :class:`~bodhilib.Splitter`, :class:`~bodhilib.Embedder` as input.

   Defined as `TextLike | List[TextLike] | Dict[str, Any] | List[Dict[str, Any]]`.

   Service supporting SerializedInput can take in::
      - a string, the string value is treated as "text" for target object, remaining values are set as defaults
      - a list of strings, created iteratively same as above
      - an object supporting :class:`~bodhilib.SupportsText`, the property `text` is treated as "text" for the target object, remaining values are set as defaults
      - a list of objects supporting :class:`~bodhilib.SupportsText`, created iteratively same as above
      - a serialized object as :class:`dict`, e.g. for :class:`~bodhilib.Prompt` can be `{"text": "hello", "role": "user", "source": "input"}`. The input is passed to the constructor and built using :class:`~pydantic.main.BaseModel` implementation.
      - a list of serialized objects as :class:`dict`, created iteratively same as above

.. data:: bodhilib.Embedding

   Type alias for `List[float]`, to indicate the embedding generated from :class:`~bodhilib.Embedder` operation.

.. automodule:: bodhilib
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __iter__
   :private-members: _embed, _split, _StrEnumMixin

.. data:: bodhilib.TemplateFormat

   List of possible values for TemplateFormat

.. data:: bodhilib.C

   TypeVar for bodhilib Components

.. data:: bodhilib.T

   TypeVar for LLM API response
   
.. data:: bodhilib.PS

   TypeVar for type bound to :class:`~bodhilib.PromptSource`

.. data:: bodhilib.DL

   TypeVar for type bound to :class:`~bodhilib.DataLoader`

.. data:: bodhilib.S

   TypeVar for type bound to :class:`~bodhilib.Splitter`

.. data:: bodhilib.E

   TypeVar for type bound to :class:`~bodhilib.Embedder`

.. data:: bodhilib.L

   TypeVar for type bound to :class:`~bodhilib.LLM`

.. data:: bodhilib.V

   TypeVar for type bound to :class:`~bodhilib.VectorDB`

.. class:: bodhilib._models._StrEnumMixin

   Mixin class to support string enums
