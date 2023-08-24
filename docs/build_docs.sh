#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail
set -o xtrace

# Build the api documentation
# poetry run sphinx-apidoc --force --implicit-namespaces --module-first -o docs/reference/ libs/bodhilib/bodhilib libs/bodhilib.cohere/bodhilib
# poetry run sphinx-apidoc -o docs/reference libs/bodhilib/bodhilib
rm -rf docs/reference/_autosummary
poetry run sphinx-apidoc --implicit-namespaces -o docs/reference libs/bodhilib.cohere/bodhilib
poetry run sphinx-apidoc --implicit-namespaces -o docs/reference libs/bodhilib/bodhilib

SCRIPT_DIR="$(cd "$(dirname "$0")"; pwd)"
cd "${SCRIPT_DIR}"

# Build the documentation
poetry run sphinx-build -a -E -j auto -n --color -W --keep-going -b html . _build/

# Check links in the documentation
poetry run sphinx-build -b linkcheck . _build/linkcheck/
