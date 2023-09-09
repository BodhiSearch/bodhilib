Setting up guiding principles for designing the library, so there is an overall consistency in design.


# Prefer Iterable/List of inputs over two different methods of a single item vs list of items

### Advantages
- No need to have multiple methods with similar names, e.g. `embed` vs `embeds`
- Have consistent return type, hence consistent processing of outputs

E.g. bodhilib.embedder.Embedder have method embed with type signature - 
`def embed(self, texts: List[TextLike]) -> List[List[float]]`
It takes in a list of TextLike objects to embed. So you can pass it a list of strings like `embed(["hello", "world"])`. In case you need to process single string, just create a list on the fly like `embed(["hello"])`
