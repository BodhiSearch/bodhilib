import itertools

from bodhilib import Distance, Role, Source

default_system_prompt = (
    "Answer my question below based on best of your ability. " + "Say no if you don't know the answer."
)
default_user_prompt = "Question: What day of the week comes after Monday?\nAnswer: "
gpt35turbo = "gpt-3.5-turbo"


roles = [Role.USER, Role.AI, Role.SYSTEM]
roles_str = ["user", "ai", "system"]
sources = [Source.INPUT, Source.OUTPUT]
sources_str = ["input", "output"]
distances = [Distance.COSINE, Distance.EUCLIDEAN, Distance.DOT_PRODUCT]
distances_str = ["cosine", "euclidean", "dot_product"]

all_enum_str = list(itertools.chain(*map(zip, [roles, sources, distances], [roles_str, sources_str, distances_str]))) # type: ignore
