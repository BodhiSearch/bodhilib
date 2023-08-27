#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail
set -o xtrace

# Build the api documentation
# rm -rf docs/reference/_autosummary
poetry run sphinx-apidoc --implicit-namespaces --separate --module-first -o docs/api/reference libs/bodhilib/src/bodhilib
poetry run sphinx-apidoc --implicit-namespaces --separate --module-first -o docs/api/reference libs/bodhilib.cohere/src/bodhilib

SCRIPT_DIR="$(cd "$(dirname "$0")"; pwd)"
cd "${SCRIPT_DIR}"

# Build the documentation
poetry run sphinx-build -a -E -j auto -n --color -W --keep-going -b html api api/_build/

# Check links in the documentation
poetry run sphinx-build -b linkcheck api api/_build/linkcheck/
