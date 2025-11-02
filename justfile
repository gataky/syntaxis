# justfile

# Format python code
format:
    autoflake --in-place --remove-all-unused-imports --recursive .
    isort .
    black .
