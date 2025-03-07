dist/main.exe: main.py .venv
    uv run pyinstaller main.spec

.venv:
    uv sync