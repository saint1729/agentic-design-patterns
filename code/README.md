Code examples for chapters

Organize runnable examples under `code/chapter_XX/`. Each chapter folder should contain:

- `<pattern>.py` — example scripts
- `requirements.txt` — Python dependencies for the examples
- `.env` (local, not committed) — secrets for running examples
- `.venv` (local, not committed) - virtual environment for running examples

Quick commands (one-liners)

- Create a chapter venv and install its requirements:

```bash
bash code/setup_venv.sh chapter_01        # creates code/chapter_01/.venv
source code/chapter_01/.venv/bin/activate  # activate
```


- Run the chapter example:

```bash
python prompt_chaining.py
```

Environment variables

- Use `code/.env.example` as a template. Copy it into the chapter folder and fill your secrets:

```bash
cp code/.env.example code/chapter_01/.env
# edit code/chapter_01/.env and fill OPENAI_API_KEY (do NOT commit)
```

Security notes

- Never commit `.env` files. The repository ignores `.env` by default.
- For CI, store secrets in your CI provider and inject them at runtime.

Customizing workflow

- If you prefer Conda environments instead of venvs, activate the Conda env and `pip install -r code/chapter_01/requirements.txt` instead of creating a venv.
- `code/setup_venv.sh` supports a `PYTHON` override to control the interpreter used to create the venv.
