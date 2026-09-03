# Operations

## Local setup

1. Install Python 3.10–3.13 and `uv`.
2. Run `uv sync`.
3. Copy `.env.example` to `.env`, set `SERPER_API_KEY`, and configure at least one runtime model key: `GEMINI_API_KEY`, `GROQ_API_KEY`, or `OPENROUTER_API_KEY`. Add Pushover credentials only if notifications are required.
4. Run `uv run crewai run`.

For the web interface, run `uv run python app.py` and open `http://127.0.0.1:7860`. Override the port with `PORT`; production services must expose that same environment-provided port.

Generated files in `output/` and `sandbox*/` are local artifacts and are excluded from publication.

At runtime, missing model-provider keys are skipped and the configured providers are tried in quality order. If all configured providers fail, the error lists each attempted provider without exposing credentials. Missing Pushover credentials disable only the notification; report generation continues.

## Verification

Run `./scripts/verify.sh`, or on Windows run `uv run python scripts/verify.py`.

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
