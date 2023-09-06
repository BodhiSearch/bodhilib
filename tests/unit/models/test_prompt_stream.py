from bodhilib.models import Prompt, PromptStream, Role, Source, prompt_output


def test_returns_a_prompt_stream():
    stream = PromptStream(iter(["this ", "is ", "a ", "prompt ", "stream."]), lambda x: prompt_output(x))
    outputs = list(stream)
    assert len(outputs) == 5
    assert outputs[0] == Prompt("this ", role=Role.AI, source=Source.OUTPUT)
    assert outputs[1] == prompt_output("is ")
    assert outputs[2] == prompt_output("a ")
    assert outputs[3] == prompt_output("prompt ")
    assert outputs[4] == prompt_output("stream.")
    assert stream.text == "this is a prompt stream."
