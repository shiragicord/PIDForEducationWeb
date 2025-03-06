dist/main.exe: src/main.py .venv
    uv run pyinstaller main.spec

.venv:
    uv sync