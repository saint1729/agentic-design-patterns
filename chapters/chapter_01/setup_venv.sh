#!/usr/bin/env bash
set -euo pipefail

# Run from inside the chapter folder. Creates a local .venv inside this folder.
python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

echo "\nChapter environment ready. Activate with: source .venv/bin/activate"
