{-# LANGUAGE DuplicateRecordFields #-}

module Domain where

-- prompt
data Role = System | AI | User deriving (Eq, Show)

data Source = Input | Output deriving (Eq, Show)

data Prompt = Prompt {text :: String, role :: Role, source :: Source} deriving (Eq, Show)

promptFromString :: String -> Prompt
promptFromString text = Prompt {text = text, role = User, source = Input}

type PromptStream = [Prompt]

data PromptTemplate = PromptTemplate {template :: String, role :: Role, source :: Source, engine :: String, args :: [(String, String)]}

createTemplate :: (String, Role, Source, String, [(String, String)]) -> PromptTemplate
createTemplate (template, role, source, engine, args) = PromptTemplate {template = template, role = role, source = source, engine = engine, args = args}

process :: String -> String -> [(Role, String)]
process engine template = [(User, template)]

data PromptInput = FromPrompt Prompt | FromPrompts [Prompt] | FromString String

-- trait to convert a prompt to a prompt input
-- not needed by python because of dynamic nature
class ToPromptInput a where
  toPromptInput :: a -> PromptInput

instance ToPromptInput Prompt where
  toPromptInput = FromPrompt

instance ToPromptInput [Prompt] where
  toPromptInput = FromPrompts

instance ToPromptInput String where
  toPromptInput = FromString

instance ToPromptInput PromptTemplate where
  toPromptInput :: PromptTemplate -> PromptInput
  toPromptInput pt = toPromptInput [Prompt {text = text, role = role, source = Input} | (role, text) <- outputs]
    where
      outputs = process (engine pt) (template pt)

-- to convert prompt inputs back to prompt list for processing
toPrompts :: PromptInput -> [Prompt]
toPrompts (FromPrompt p) = [p]
toPrompts (FromPrompts ps) = ps
toPrompts (FromString s) = [promptFromString s]

withExamples :: String -> [(String, String)] -> PromptTemplate
withExamples template args = PromptTemplate {template = template, role = User, source = Input, engine = "jinja2", args = args}

-- document
data Document = Document {text :: String, metadata :: [(String, String)]}
  deriving (Show)

type Embedding = [Float]

data Node = Node {id :: String, text :: String, parent :: Document, metadata :: [(String, String)], embedding :: Embedding}
  deriving (Show)

nodeEmbedding (Node {embedding}) = embedding

-- data loader
class DataLoader a where
  load :: a -> [String] -> [Document]

data FileDataLoader = FileDataLoader

instance DataLoader FileDataLoader where
  load :: FileDataLoader -> [String] -> [Document]
  load FileDataLoader paths = [Document {text = t, metadata = []} | t <- paths]

-- llm
class LLM a where
  generate :: a -> PromptInput -> Prompt

data OpenAILLM = LLM

concatenatePrompts :: [Prompt] -> String
concatenatePrompts prompts = unwords (map getText prompts)
  where
    getText (Prompt {text}) = text

instance LLM OpenAILLM where
  generate :: OpenAILLM -> PromptInput -> Prompt
  generate openai promptInput = Prompt {text = "Hello " ++ request, source = Output, role = User}
    where
      prompts = toPrompts promptInput
      request = concatenatePrompts prompts

-- splitter
data Documents' = Doc Document | Docs [Document]

class Splitter a where
  split :: a -> Documents' -> [Node]

data TextSplitter = TextSplitter

instance Splitter TextSplitter where
  split :: TextSplitter -> Documents' -> [Node]
  split ts (Doc doc) = [Node {id = "123", text = t, parent = doc, metadata = [], embedding = [0.0]} | t <- words (getText doc)]
    where
      getText (Document {text}) = text
  split ts (Docs docs) = [Node {id = "", text = t, parent = doc, metadata = [], embedding = [0.0]} | doc <- docs, t <- words (getText doc)]
    where
      getText (Document {text}) = text

-- embedder
class Embedder a where
  embed :: a -> [Node] -> [Node]

data OpenAIEmbedder = OpenAIEmbedder

instance Embedder OpenAIEmbedder where
  embed :: OpenAIEmbedder -> [Node] -> [Node]
  embed openai nodes = [n {embedding = [1.0 .. 10.0]} | n <- nodes]

-- vectordb
data Distance = Cosine | Euclid | Dot

data VectorDBConfig = VectorDBConfig {name :: String, dimension :: Int, distance :: Distance}

type Collection = String

data VectorQuery = VectorQuery {embedding :: Embedding, filter :: Maybe [(String, String)]}

vectorQuery :: Node -> VectorQuery
vectorQuery (Node {embedding}) = VectorQuery {embedding = embedding, filter = Nothing}

class VectorDB a where
  getCollections :: a -> [Collection]
  createCollection :: a -> VectorDBConfig -> Collection
  upsert :: a -> Collection -> [Node] -> [Node]
  query :: a -> Collection -> VectorQuery -> [Node]

data Pinecone = Pinecone

instance VectorDB Pinecone where
  getCollections :: Pinecone -> [Collection]
  getCollections pinecone = []

  createCollection :: Pinecone -> VectorDBConfig -> Collection
  createCollection pinecone config = ""

  upsert :: Pinecone -> Collection -> [Node] -> [Node]
  upsert pinecone collection nodes = nodes

  query :: Pinecone -> Collection -> VectorQuery -> [Node]
  query pinecone collection query = []
