#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
ENV_DIR="${UNSLOTH_ENV_DIR:-${REPO_ROOT}/training/.venv-unsloth}"
REQ_FILE="${REPO_ROOT}/training/requirements-unsloth.txt"
PYTHON_BIN="${PYTHON_BIN:-python3.12}"

case "${ENV_DIR}" in
  "${REPO_ROOT}/backend"*|"${REPO_ROOT}/frontend"*)
    echo "Refusing to create the Unsloth training environment inside app runtime directories: ${ENV_DIR}" >&2
    exit 2
    ;;
esac

if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  PYTHON_BIN="python3"
fi

echo "Creating isolated Unsloth training environment at ${ENV_DIR}"
"${PYTHON_BIN}" -m venv "${ENV_DIR}"

# shellcheck source=/dev/null
source "${ENV_DIR}/bin/activate"

python -m pip install --upgrade pip uv

if command -v uv >/dev/null 2>&1; then
  uv pip install -r "${REQ_FILE}" --torch-backend=auto
else
  python -m pip install -r "${REQ_FILE}"
fi

echo
echo "Training environment ready for verification."
echo "Activate with: source training/.venv-unsloth/bin/activate"
echo "Check with:    python training/scripts/check_training_env.py"
