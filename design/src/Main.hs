module Main (main) where

import Control.Arrow ((>>>))
import Domain

llm = LLM

-- get
prompt = promptFromString " world"

inputAsStr = generate llm (toPromptInput " world")

inputAsPrompt = generate llm (toPromptInput prompt)

inputAsPrompts = generate llm (toPromptInput [prompt, prompt])

-- generate with compose
inputAsCompose = (generate llm . toPromptInput) "hello"

outputFromArrow = (toPromptInput >>> generate llm) "arrow"

-- from template
pt = createTemplate (" world", User, Input, "jinja2", [("examples", "values")])

inputAsTemplate = generate llm (toPromptInput pt)

templateAsCompose = (generate llm . toPromptInput . createTemplate) (" world", User, Input, "jinja2", [("examples", "values")])

templateAsArrow = (createTemplate >>> toPromptInput >>> generate llm) (" template arrow", User, Input, "jinja2", [("examples", "values")])

-- convert files to document
f = FileDataLoader

-- get docs
docs = load f ["hello", "world"]

-- get nodes
nodes = split TextSplitter (Docs docs)

embeddings = embed OpenAIEmbedder nodes

-- insert embeddings

records = upsert Pinecone "my_collection" embeddings

result = query Pinecone "my_collection" $ vectorQuery (head records)

-- composing
recordCompose = (upsert Pinecone "my_collection" . embed OpenAIEmbedder . split TextSplitter . Docs . load f) ["hello", "world"]

main :: IO ()
main = do
  print $ "hello" ++ "world"
  print $ "inputAsStr = " ++ show inputAsStr
  print $ "inputAsPrompt = " ++ show inputAsPrompt
  print $ "inputAsPrompt = " ++ show inputAsPrompt
  print $ "inputAsPrompts = " ++ show inputAsPrompts
  print $ "inputAsCompose = " ++ show inputAsCompose
  print $ "outputFromArrow = " ++ show outputFromArrow
  print $ "templateAsCompose = " ++ show templateAsCompose
  print $ "templateAsArrow = " ++ show templateAsArrow
  print $ "records = " ++ show records
  print $ "result = " ++ show result
  print $ "recordCompose = " ++ show recordCompose
