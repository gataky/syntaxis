# justfile

# Format python code
format:
    autoflake --in-place --remove-all-unused-imports --recursive .
    isort .
    black .

# Reset and seed the database
seed:
    python -m syntaxis.cli create-db --clear
    python -m syntaxis.cli seed-dictionary
    python -m syntaxis.cli seed-pronouns
    python -m syntaxis.cli seed-articles

# Setup the development environment from a fresh start
fresh:
    rm -rf .venv
    uv venv .venv
    uv sync --all-extras
    uv pip install -e .

dev:
    uvicorn syntaxis:app --reload --port 5000

web:
    cd client && npm run dev
