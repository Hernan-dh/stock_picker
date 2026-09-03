# Architecture

## Purpose

`stock_picker` is a CrewAI project whose agents and tasks are configured in YAML and orchestrated from Python.
The runtime is pinned to CrewAI 1.15.18 for reproducible execution.

## Components

- `src/stock_picker/config/agents.yaml`: agent roles, goals, and backstories.
- `src/stock_picker/config/tasks.yaml`: task descriptions and expected outputs.
- `src/stock_picker/crew.py`: CrewAI agent, task, and crew construction.
- `src/stock_picker/model_config.py`: version-controlled, quality-ordered model configuration.
- `src/stock_picker/model_provider.py`: shared per-call fallback across Gemini, Groq, and OpenRouter.
- `src/stock_picker/main.py`: command-line entry points and kickoff inputs.
- `knowledge/`: versioned knowledge supplied to the crew.
- `output/` and `sandbox*/`: generated execution artifacts excluded from Git.
- `scripts/`: shared verification, documentation, hook installation, and safe publishing commands.

## Trust boundaries

- Prompts, model responses, tool results, generated code, and generated reports are untrusted.
- Credentials are loaded from the environment and must not enter Git, prompts, logs, or documentation.
- CrewAI model and tool providers are external services.

## Model resilience

All agents, including the hierarchical manager, share one CrewAI-compatible fallback LLM. Each model call tries the configured free-tier options in order: Gemini 3.7 Flash, Gemini 3.6 Flash, Groq-hosted GPT-OSS 120B, then OpenRouter-hosted NVIDIA Nemotron 3 Super Free. A provider failure retries only that call and preserves completed task output. Model calls allow up to 16,384 output tokens.

CrewAI memory is intentionally disabled because its default embedding path can require an unrelated OpenAI credential. Serper remains the external source for current financial news and market research.

## Related decisions

- [Continuous documentation and safe publishing](decisions/0001-continuous-documentation-and-safe-publishing.md)
