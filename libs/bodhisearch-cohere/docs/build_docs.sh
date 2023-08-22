#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail
set -o xtrace

# Build the api documentation
rm -rf docs/reference
poetry run sphinx-apidoc --force --implicit-namespaces --module-first -o docs/reference/ bodhisearch_cohere/

SCRIPT_DIR="$(cd "$(dirname "$0")"; pwd)"
cd "${SCRIPT_DIR}"

# Build the documentation
poetry run sphinx-build -a -E -j auto -n --color -W --keep-going -b html . _build/

# Check links in the documentation
poetry run sphinx-build -b linkcheck . _build/linkcheck/
