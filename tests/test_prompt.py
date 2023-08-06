from bodhisearch.prompt import Prompt, parse_prompts

default_system_prompt = (
    "Answer my question below based on best of your ability. "
    + "Say no if you don't know the answer."
)
default_user_prompt = (
    "Question: What day of the week comes after Monday?\nAnswer: "
)


def test_parse_prompt_from_str():
    prompts = parse_prompts(default_user_prompt)
    assert len(prompts) == 1
    assert prompts[0] == Prompt(default_user_prompt)


def test_empty_list():
    prompts = parse_prompts([])
    assert prompts == []


def test_parse_prompt_from_list_of_str():
    prompts = parse_prompts([default_user_prompt])
    assert len(prompts) == 1
    assert prompts[0] == Prompt(default_user_prompt)


def test_parse_prompt_from_prompt():
    input = Prompt(default_user_prompt)
    prompts = parse_prompts(input)
    assert len(prompts) == 1
    assert prompts[0] == input


def test_parse_prompt_from_dict():
    input = {"text": default_user_prompt}
    prompts = parse_prompts(input)
    assert len(prompts) == 1
    assert prompts[0] == Prompt(default_user_prompt, "user")


def test_parse_prompt_from_dict_full():
    input = {"text": default_system_prompt, "role": "system"}
    prompts = parse_prompts(input)
    assert len(prompts) == 1
    assert prompts[0] == Prompt(default_system_prompt, "system")


def test_parse_prompt_mix():
    prompts = parse_prompts(
        [
            default_user_prompt,
            {"text": default_system_prompt, "role": "system"},
            Prompt(default_user_prompt, "system"),
        ]
    )
    assert len(prompts) == 3
    assert prompts[0] == Prompt(default_user_prompt)
    assert prompts[1] == Prompt(default_system_prompt, "system")
    assert prompts[2] == Prompt(default_user_prompt, "system")
