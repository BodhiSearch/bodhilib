#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail
set -o xtrace

# Build the api documentation
# rm -rf docs/reference/_autosummary
poetry run sphinx-apidoc --implicit-namespaces --separate --module-first -o docs/reference libs/bodhilib.cohere/bodhilib
poetry run sphinx-apidoc --implicit-namespaces --separate --module-first -o docs/reference libs/bodhilib/src/bodhilib

SCRIPT_DIR="$(cd "$(dirname "$0")"; pwd)"
cd "${SCRIPT_DIR}"

# Build the documentation
poetry run sphinx-build -a -E -j auto -n --color -W --keep-going -b html . _build/

# Check links in the documentation
poetry run sphinx-build -b linkcheck . _build/linkcheck/
