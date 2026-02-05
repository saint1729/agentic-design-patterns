#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: $0 <chapter-folder>

Examples:
  $0 chapter_01       # from repository root (will resolve to code/chapter_01)
  $0 code/chapter_01  # explicit path"
  exit 1
}

if [ "$#" -ne 1 ]; then
  usage
fi

TARGET="$1"

# Accept either a bare chapter name or a path under code/
if [ ! -d "$TARGET" ]; then
  if [ -d "code/$TARGET" ]; then
    TARGET="code/$TARGET"
  elif [ -d "chapters/$TARGET" ]; then
    TARGET="chapters/$TARGET"
  else
    echo "Target folder '$TARGET' not found in workspace." >&2
    exit 1
  fi
fi

# Create virtualenv using the requested python interpreter.
# You can override which python to use by setting the `PYTHON` environment variable,
# e.g. `PYTHON=/opt/anaconda3/bin/python bash code/setup_venv.sh chapter_01`.
echo "Creating virtualenv inside: $TARGET/.venv"
PYTHON_CMD="${PYTHON:-python}"
if ! command -v "$PYTHON_CMD" >/dev/null 2>&1; then
  echo "Python executable '$PYTHON_CMD' not found; falling back to 'python3'"
  PYTHON_CMD=python3
fi
echo "Using interpreter: $($PYTHON_CMD --version 2>&1 | tr -d '\n') ($PYTHON_CMD)"
"$PYTHON_CMD" -m venv "$TARGET/.venv"
# shellcheck disable=SC1091
source "$TARGET/.venv/bin/activate"
python -m pip install --upgrade pip setuptools wheel

if [ -f "$TARGET/requirements.txt" ]; then
  echo "Installing requirements from $TARGET/requirements.txt"
  pip install -r "$TARGET/requirements.txt"
else
  echo "No requirements.txt found in $TARGET — skipping pip install."
fi

echo "Installing python-dotenv into the chapter virtualenv"
pip install python-dotenv

echo "\nDone. Activate with:\n  source \"$TARGET/.venv/bin/activate\""
echo "Run code from: $TARGET"
