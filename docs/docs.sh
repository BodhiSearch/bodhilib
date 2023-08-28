#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail
set -o xtrace

SCRIPT_DIR="$(cd "$(dirname "$0")"; pwd)"
cd "${SCRIPT_DIR}"

# Build the api documentation
# rm -rf reference/_autosummary
poetry run sphinx-apidoc --implicit-namespaces --separate --module-first -o api/reference ../src/bodhilib
poetry run sphinx-apidoc --implicit-namespaces --separate --module-first -o api/reference ../libs/bodhilib.cohere/src/bodhilib

# Build the documentation
poetry run sphinx-build -a -E -j auto -n --color -W --keep-going -b html api api/_build/

# Check links in the documentation
poetry run sphinx-build -b linkcheck api api/_build/linkcheck/
