bodhilib.models package
=======================

.. automodule:: bodhilib.models
   :members:
   :undoc-members:
   :show-inheritance:
   :exclude-members: parse_prompts

.. py:data:: PromptInput

   Represents the type for various input types that can be passed as prompt.

   Defined as `Union[str, List[str], :class:Prompt, List[Prompt], Dict[str, Any], List[Dict[str, Any]]]`.

   When defined using Dict, should represent the serialized form of :class:`Prompt`. E.g.::

       {
           "text": "your prompt",
           "role": "user",
           "source": "input",
       }

.. py:function:: parse_prompts(prompts: PromptInput) -> List[Prompt]

.. py:function:: parse_prompts(prompts: Union[str, List[str], Prompt, List[Prompt], Dict[str, Any], List[Dict[str, Any]]]) -> List[Prompt]

   Parses from the :data:`PromptInput` to List[:class:`Prompt`].
