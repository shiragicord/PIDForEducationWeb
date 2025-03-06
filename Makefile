dist/main.exe: src/main.py .venv
    uv run pyinstaller --onefile --noconsole src/main.py
    cp -r res dist/

.venv:
    uv sync