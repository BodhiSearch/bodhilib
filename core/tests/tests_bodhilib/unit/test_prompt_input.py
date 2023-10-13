from bodhilib import Prompt, to_prompt_list

from tests_bodhilib.prompt_utils import default_system_prompt, default_user_prompt


def test_parse_prompt_from_str():
    prompts = to_prompt_list(default_user_prompt)
    assert len(prompts) == 1
    assert prompts[0] == Prompt(default_user_prompt)


def test_parse_prompt_empty_list():
    prompts = to_prompt_list([])
    assert prompts == []


def test_parse_prompt_from_list_of_str():
    prompts = to_prompt_list([default_user_prompt])
    assert len(prompts) == 1
    assert prompts[0] == Prompt(default_user_prompt)


def test_parse_prompt_from_prompt():
    input = Prompt(default_user_prompt)
    prompts = to_prompt_list(input)
    assert len(prompts) == 1
    assert prompts[0] == input


def test_parse_prompt_from_dict():
    input = {"text": default_user_prompt}
    prompts = to_prompt_list(input)
    assert len(prompts) == 1
    assert prompts[0] == Prompt(default_user_prompt, "user")


def test_parse_prompt_from_dict_full():
    input = {"text": default_system_prompt, "role": "system"}
    prompts = to_prompt_list(input)
    assert len(prompts) == 1
    assert prompts[0] == Prompt(default_system_prompt, "system")


def test_parse_prompt_mix():
    prompts = to_prompt_list(
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
