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

# Setup the development environment
setup:
    rm -rf .venv
    ASDF_PYTHON=$(asdf which python) && \
    uv venv --python "$ASDF_PYTHON" .venv && \
    UV_PROJECT_ENVIRONMENT=.venv uv sync --all-extras && \
    UV_PROJECT_ENVIRONMENT=.venv uv pip install -e .

dev:
    uv run uvicorn syntaxis.service.app:app --reload --port 5000
