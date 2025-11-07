# Repository Guidelines

## Project Structure & Module Organization
- `battle/engine.py` holds the core simulation loop (`BattleEngine`) and is responsible for round order, RNG seeding, and statistics.
- `characters/` contains the abstract base class (`base.py`), concrete fighters (currently `sample.py` with 布洛妮娅、琪亚娜、李素裳), and the public exports in `__init__.py`.
- `main.py` wires matchups together, prints aggregate win rates, and runs optional verbose single battles. Keep ad‑hoc prototypes here or in new top-level scripts; avoid mixing experiment code into modules.

## Build, Test, and Development Commands
- `python3 main.py` — runs the configured matchups for 10 000 battles each and prints summary + verbose logs.
- `uv run python main.py` — equivalent invocation when you have `uv` environments configured; uses `.python-version` to pin Python 3.13.
- `uv pip install -r requirements.txt` (if added later) — preferred way to manage dependencies; keep them listed under `[project]` in `pyproject.toml`.

## Coding Style & Naming Conventions
- Follow PEP 8: 4-space indentation, snake_case for functions/variables, PascalCase for classes.
- Keep gameplay constants (damage values, proc rates) near the class definitions; document non-obvious math with short comments.
- All user-facing text (CLI output, logs) should remain in中文 unless there is a strong reason otherwise.

## Testing Guidelines
- There is no automated test suite yet; rely on `python3 main.py` for regression checks before submitting.
- When adding deterministic scenarios, seed the `BattleEngine` to keep results reproducible.
- If you introduce formal tests, place them under `tests/` with `pytest`-style `test_*.py` files and update this guide with run instructions.

## Commit & Pull Request Guidelines
- Write imperative, succinct commit subjects (e.g., “Add LiSushang bleed hooks”) and group related edits together.
- Describe behavioral changes in the commit body or PR description: include matchup impact, new commands, and any data files touched.
- PRs should link relevant issues, summarize verification steps (`python3 main.py`, manual logs), and include screenshots of CLI output when visual clarity helps.
