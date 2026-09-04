# StockPicker Crew

Welcome to the StockPicker Crew project, powered by [crewAI](https://crewai.com). This template is designed to help you set up a multi-agent AI system with ease, leveraging the powerful and flexible framework provided by crewAI. Our goal is to enable your agents to collaborate effectively on complex tasks, maximizing their collective intelligence and capabilities.

## Installation

Ensure you have Python >=3.10 <3.14 installed on your system. This project uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling, offering a seamless setup and execution experience.

First, if you haven't already, install uv:

```bash
pip install uv
```

Next, navigate to your project directory and install the dependencies:

(Optional) Lock the dependencies and install them by using the CLI command:
```bash
crewai install
```
### Customizing

Configure `SERPER_API_KEY`, plus at least one of `GEMINI_API_KEY`, `GROQ_API_KEY`, or `OPENROUTER_API_KEY` in `.env`. Pushover credentials are required only if you want the final notification.

- Modify `src/stock_picker/config/agents.yaml` to define your agents
- Modify `src/stock_picker/config/tasks.yaml` to define your tasks
- Modify `src/stock_picker/crew.py` to add your own logic, tools and specific args
- Modify `src/stock_picker/main.py` to add custom inputs for your agents and tasks

## Running the Project

To kickstart your crew of AI agents and begin task execution, run this from the root folder of your project:

```bash
$ crewai run
```

This command initializes the stock_picker Crew, assembling the agents and assigning them tasks as defined in your configuration.

Every agent uses the same quality-first, per-call model fallback: Gemini 3.7 Flash, Gemini 3.6 Flash, Groq GPT-OSS 120B, and OpenRouter NVIDIA Nemotron 3 Super Free. Failed or repetitive responses move to the next provider. Missing provider keys are skipped. Pushover notifications are also skipped cleanly when their optional credentials are absent.

To run the bilingual Gradio interface:

```bash
uv run python app.py
```

Open `http://127.0.0.1:7860`. The interface accepts a market sector and returns the crew's final stock selection report.

This example, unmodified, will run the create a `report.md` file with the output of a research on LLMs in the root folder.

## Understanding Your Crew

The stock_picker Crew is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of tasks, defined in `config/tasks.yaml`, leveraging their collective skills to achieve complex objectives. The `config/agents.yaml` file outlines the capabilities and configurations of each agent in your crew.

## Support

For support, questions, or feedback regarding the StockPicker Crew or crewAI.
- Visit our [documentation](https://docs.crewai.com)
- Reach out to us through our [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join our Discord](https://discord.com/invite/X4JWnZnxPb)
- [Chat with our docs](https://chatg.pt/DWjSBZn)

Let's create wonders together with the power and simplicity of crewAI.
