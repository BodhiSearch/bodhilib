#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail
set -o xtrace

SCRIPT_DIR="$(cd "$(dirname "$0")"; pwd)"
cd "${SCRIPT_DIR}"

# Build the documentation
poetry run sphinx-build -a -E -j auto -n --color -W --keep-going -b html guides guides/_build

# Check links in the documentation
poetry run sphinx-build -b linkcheck guides guides/_build/linkcheck/
