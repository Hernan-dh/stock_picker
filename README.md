# Stock Picker

A bilingual research assistant that finds trending companies in a sector, researches them, and proposes one candidate with supporting reasoning.

## Attribution

Project built from [Ed Donner's agentic AI engineering course](https://github.com/ed-donner/agents). The upstream MIT copyright notice is preserved in [LICENSE](LICENSE). No endorsement by the course author is implied.

## Run locally

Python 3.12 and uv are the documented development baseline.  Run the following commands from this repository's root.

```sh
uv sync
```

Copy `.env.example` to `.env` (`Copy-Item .env.example .env` in PowerShell, or `cp .env.example .env` on Linux/macOS), then replace only the placeholders for the providers you intend to use. Leave unused credentials empty. Never commit the real `.env`.

Configure `SERPER_API_KEY` and at least one model-provider key. Open `http://127.0.0.1:7860` and enter a market sector. Use `uv run crewai run` for the CLI.

```sh
uv run python app.py
```

## Download results

After a request completes, choose Markdown (.md), Word (.docx) or PDF (.pdf),
then select **Prepare download** and click the generated file. Spanish controls
use **Preparar descarga**. Downloads contain the last completed report in that
chat, including sources. Starting another request clears the previous download.

Markdown preserves the original result. DOCX and PDF retain headings, lists,
tables and source URLs with a simplified layout; they do not reproduce the chat
styling or fetch external images. PDF uses an embedded font for English and
Spanish; glyph coverage for other scripts is limited. Files are temporary, so
save a local copy.

## Architecture

```text
Gradio / CLI sector -> company finder -> structured research -> candidate selection -> report
```

See [architecture](docs/ARCHITECTURE.md) for components, data flow and trust boundaries, and [operations](docs/OPERATIONS.md) for configuration and recovery.

## Technologies

Python, CrewAI, Gradio 6, Pydantic, Serper, YAML, uv and unittest; Gemini, Groq and OpenRouter model providers.

## Reproducible tests

After installing the dependencies above:

```sh
uv run python -m unittest discover -v
uv run python scripts/verify.py
```

Coverage: Repetitive-response rejection and rate-limit parsing, plus real Gradio message serialization, repeated turns and error recovery with backend calls mocked. Tests run without real credentials or paid API calls. They do not measure model quality, live provider availability, or full browser behavior. CI installs dependencies and runs the same verifier on pushes and pull requests.

## Limitations

The selection is an unvalidated model judgment, not investment advice or a return forecast. There is no backtest, trading connection or real-time price feed. Bounded searches can miss relevant companies. Requests are independent and generated output paths are shared. Public operation needs authentication, usage limits and isolated output storage.

Prompts and relevant context are sent to external model/search providers. Do not submit secrets or confidential data. Provider names in source code are configuration, not promises of current availability, pricing, or free access.

## Public repository and license

The repository includes a placeholder-only [.env.example](.env.example); local credentials, caches and generated artifacts are excluded by [.gitignore](.gitignore). See [operations](docs/OPERATIONS.md) for verification and publication instructions.

The code is distributed under the [MIT license](LICENSE). Dependencies retain their own licenses. Biographical material, third-party documents, logos and linked content are not relicensed by this code license. Publishing scripts can send code diffs to external models when generating commit text; use explicit metadata to avoid that step.
