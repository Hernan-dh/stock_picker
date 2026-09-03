#!/usr/bin/env sh
set -eu

root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)

works() {
    "$@" -c 'import sys; raise SystemExit(sys.version_info < (3, 9))' >/dev/null 2>&1
}

if [ -f "$root/.venv/bin/python" ] && works "$root/.venv/bin/python"; then
    python="$root/.venv/bin/python"
elif [ -f "$root/.venv/Scripts/python.exe" ] && works "$root/.venv/Scripts/python.exe"; then
    python="$root/.venv/Scripts/python.exe"
elif command -v python3 >/dev/null 2>&1 && works python3; then
    python=python3
elif command -v python >/dev/null 2>&1 && works python; then
    python=python
elif command -v py >/dev/null 2>&1 && works py -3; then
    exec py -3 "$root/scripts/verify.py"
else
    echo "Python 3 was not found." >&2
    exit 1
fi

exec "$python" "$root/scripts/verify.py"
