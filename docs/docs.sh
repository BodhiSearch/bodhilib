#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail
set -o xtrace

SCRIPT_DIR="$(cd "$(dirname "$0")"; pwd)"
cd "${SCRIPT_DIR}"

# Build the api documentation
# rm -rf reference/_autosummary
for plugin in ../libs/*; do
  if [ -d "$plugin" ]; then
    poetry run sphinx-apidoc --implicit-namespaces --separate --module-first --templatedir api/_templates -o api/reference "$plugin/src/bodhilib"
    plugin_name=$(basename "$plugin")
    last_two_lines=$(tail -n 2 "api/reference/${plugin_name}.rst")
    if [[ "$last_two_lines" != *":inherited-members: generate"* || "$last_two_lines" != *":private-members: _generate"* ]]; then
      echo -e "   :inherited-members: generate\n   :private-members: _generate" >> "api/reference/${plugin_name}.rst"
    fi
  fi
done

rm api/reference/modules.rst api/reference/bodhilib.rst

# Build the documentation
poetry run sphinx-build -a -E -j auto -n --color -W --keep-going -b html api api/_build/

# Check links in the documentation
poetry run sphinx-build -b linkcheck api api/_build/linkcheck/
