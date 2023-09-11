Setting up guiding principles for designing the library, so there is an overall consistency in design.

# Don't re-invent the wheel

Don't get into re-inventing your own fancy wheel. Use the collective knowledge gathered/filtered/worked in the past as is, or tweak to fit your use case.

E.g. filter for docs store, decided to use MongoDB filter format. Taking in Mongo format to filter docs for Vector DB search interface. Then converting it to specific format (e.g. Qdrant filter). To handle extra feature that Qdrant supports (and not supported by other Vector DBs), will have a passthrough variable. As much support common interface as possible, but have a fallback in case is not sufficient.

# Prefer Iterable/List of inputs over two different methods of a single item vs list of items

### Advantages
- No need to have multiple methods with similar names, e.g. `embed` vs `embeds`
- Have consistent return type, hence consistent processing of outputs

E.g. bodhilib.embedder.Embedder have method embed with type signature - 
`def embed(self, texts: List[TextLike]) -> List[List[float]]`
It takes in a list of TextLike objects to embed. So you can pass it a list of strings like `embed(["hello", "world"])`. In case you need to process single string, just create a list on the fly like `embed(["hello"])`



# Services are a light layer of Adapters to underlying Client Libraries

The connectors are just an adapter layer to underlying client libraries, exposing a common interface. Designing the adapters to the most prominent client library approach is going help keep the adapter layer un-complicated, and future proof.

E.g. `Qdrant` closely mimics the underlying client library class `QdrantClient`. `QdrantClient` takes in a collection_name for every request. That has influenced the interface design for VectorDB. Hence, we are taking `collection_name` argument for each of the DB related calls.

# Prefer taking a built in client, rather than building it ourselves

E.g. QdrantClient have many configs. Provide a basic version of pass-through constructor. If does not suffice, pass the built client.
