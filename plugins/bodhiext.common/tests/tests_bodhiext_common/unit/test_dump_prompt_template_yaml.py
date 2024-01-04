from bodhiext.prompt_source import dump_prompt_template_to_yaml, load_prompt_template_yaml

from tests_bodhiext_common.conftest import TEST_DATA_DIR


def test_dump_prompt_template_yaml_same_as_load(tmp_path):
  file_path = (TEST_DATA_DIR / "prompt-templates" / "multiple-templates.yaml").resolve()
  template = load_prompt_template_yaml(str(file_path))
  output_path = tmp_path / "dumped.yaml"
  dump_prompt_template_to_yaml(template, str(output_path))
  assert file_path.read_text() == output_path.read_text()
