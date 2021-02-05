#!/bin/sh

cd "$(dirname "$0")" || exit 1

# Activate python venv
echo "Loading Python virtualenv"
# shellcheck source=venv/bin/activate
. venv/bin/activate || exit 1

echo "Launching model script"
python3 ./model.py "$@"
