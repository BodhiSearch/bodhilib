import pluggy

# core services
from bodhisearch.llm import LLM as LLM
from bodhisearch.logger.logging import init_logger

# prompts
from bodhisearch.prompt import Prompt as Prompt
from bodhisearch.prompt import PromptInput as PromptInput

# schemas
from bodhisearch.schemas import Provider as Provider

package_name = "bodhisearch"

logger = init_logger()

# pluggy settings
pluggy_project_name = "bodhisearch"
provider = pluggy.HookimplMarker(pluggy_project_name)
