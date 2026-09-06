# Operations

## Local setup

1. Install Python 3.10–3.13 and `uv`.
2. Run `uv sync`.
3. Copy `.env.example` to `.env`, set `SERPER_API_KEY`, and configure at least one runtime model key: `GEMINI_API_KEY`, `GROQ_API_KEY`, or `OPENROUTER_API_KEY`.
4. Run `uv run crewai run`.

For the web interface, run `uv run python app.py` and open `http://127.0.0.1:7860`. Override the port with `PORT`; production services must expose that same environment-provided port.

Generated files in `output/` and `sandbox*/` are local artifacts and are excluded from publication.

At runtime, missing model-provider keys are skipped and the configured providers are tried in quality order. If all configured providers fail, the error lists each attempted provider without exposing credentials.

Each search returns at most four Serper results. The finder is limited to two focused searches and four CrewAI iterations; the researcher is limited to three searches and five iterations. The final picker has three iterations, leaving recovery room without unnecessary model calls. Explicit provider rate limits receive one retry only when the requested wait is ten seconds or less; daily quotas and longer waits move immediately to the next configured model.

## Verification

Run `./scripts/verify.sh`, or on Windows run `uv run python scripts/verify.py`.

The verifier runs tests through `uv run --project` so they always use this project's environment and installed `src/stock_picker` package. This also supports calling `python scripts/verify.py` or `python scripts/publish.py` with global Python. `uv` must be available on PATH; the first run may install dependencies. There is no need to activate or deactivate a virtual environment.

If `deactivate` is not recognized in PowerShell, no standard Python virtual environment is activated in that shell. If imports fail with `No module named 'stock_picker'`, run `uv sync` from the repository and retry verification. The CRLF-to-LF Git warning is informational and does not cause test failures.

Enable the repository-managed pre-commit hook once per clone with `uv run python scripts/install_hooks.py`. GitHub Actions runs the same verifier.

## Documentation

- Rebuild the changelog: `uv run python scripts/document.py changelog`.
- Create an ADR draft: `uv run python scripts/document.py decision "Decision title"`.

## Publishing

Preview a proposal with `uv run python scripts/publish.py --preview`. Interactive publication verifies the repository, proposes an English Conventional Commit title through Gemini with Groq fallback, and requires typing `PUBLISH` before staging, committing, and pushing.

Provide `--title` and `--description` to avoid external metadata generation. Commits and pushes always require explicit user authorization.

## Recovery

- If verification fails, fix every reported item and rerun it.
- If metadata generation fails, inspect the provider attempt names, verify local keys and quotas, or provide commit metadata manually.
- Never recover with a force-push.

Gradio 6 represents Chatbot input content as typed blocks. The submission handler extracts text before calling the research backend. When checking chat changes, round-trip history through Chatbot.postprocess and Chatbot.preprocess; testing only plain string dictionaries misses this conversion.

## Public-source verification

See [README](../README.md) for the reproducible setup. CI installs dependencies before invoking the verifier. Tests disable dotenv loading and provider telemetry and use synthetic inputs or mocked external calls; passing unit tests does not certify live services or production security.

The verifier invokes tests through uv in this repository so imports resolve even when verification is started from global Python. uv must be on PATH; use uv sync --locked for the committed dependency resolution.


## Publication review

Before publishing, run the verifier and review git diff and git status --short,
especially new files. Keep real credentials in local environment files or hosting
secrets, and preserve upstream license notices. Automated secret checks cover
recognizable patterns in current source files; they do not certify the absence of
secrets or scan every historical commit, remote ref, hosting log or fork. Removing
a file from the working tree does not remove it from Git history.
