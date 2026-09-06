"""Bilingual Gradio interface for the CrewAI stock picker."""

from __future__ import annotations

import os
import random
from datetime import date
from pathlib import Path

import gradio as gr
from report_export import download_controls, prepare_with_downloads, finish_with_downloads
from dotenv import load_dotenv

from stock_picker.crew import StockPicker
from stock_picker.model_provider import fallback_llm
from styles import CSS, JS

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env", override=True)

UI_TEXT = {
    "English": {
        "subtitle": "MULTI-AGENT MARKET SELECTION",
        "greeting": "Enter a market sector and I’ll research trending companies and select the strongest candidate. This is research, not financial advice.",
        "placeholder": "Enter a sector, such as Technology…",
        "submit": "Analyze",
        "instruction": "Write the complete research and final recommendation in English.",
        "error": "I couldn't complete this stock analysis. Please try again.",
        "examples": "Example sectors",
    },
    "Español": {
        "subtitle": "SELECCIÓN DE MERCADO MULTIAGENTE",
        "greeting": "Ingresá un sector del mercado e investigaré empresas en tendencia para seleccionar la candidata más sólida. Esto es investigación, no asesoramiento financiero.",
        "placeholder": "Ingresá un sector, por ejemplo Tecnología…",
        "submit": "Analizar",
        "instruction": "Escribí la investigación y la recomendación final completas en español.",
        "error": "No pude completar este análisis bursátil. Intentá nuevamente.",
        "examples": "Sectores de ejemplo",
    },
}

SECTORS = (
    "Technology", "Healthcare", "Financial Services", "Energy",
    "Consumer Discretionary", "Industrials", "Semiconductors",
    "Cybersecurity", "Renewable Energy", "Biotechnology",
)
SUGGESTED_SECTORS = random.sample(SECTORS, k=3)
SPANISH_SECTOR_LABELS = {
    "Technology": "Tecnología",
    "Healthcare": "Salud",
    "Financial Services": "Servicios financieros",
    "Energy": "Energía",
    "Consumer Discretionary": "Consumo discrecional",
    "Industrials": "Industriales",
    "Semiconductors": "Semiconductores",
    "Cybersecurity": "Ciberseguridad",
    "Renewable Energy": "Energía renovable",
    "Biotechnology": "Biotecnología",
}


def header_html(language: str) -> str:
    text = UI_TEXT.get(language, UI_TEXT["English"])
    return f"""
    <div class="stock-brand">
      <div class="stock-mark" aria-hidden="true">
        <span class="stock-bar stock-bar-1"></span>
        <span class="stock-bar stock-bar-2"></span>
        <span class="stock-bar stock-bar-3"></span>
      </div>
      <div class="stock-headings">
        <h1>STOCK<span class="stock-sep">/</span>PICKER</h1>
        <p>{text['subtitle']}</p>
      </div>
    </div>
    """


def localized_ui(language: str):
    return (
        header_html(language),
        gr.Group(visible=language == "English"),
        gr.Group(visible=language == "Español"),
    )


def initialize_language(browser_language: str):
    language = "Español" if (browser_language or "").lower().startswith("es") else "English"
    header, english_group, spanish_group = localized_ui(language)
    return language, header, english_group, spanish_group


def analyze_sector(message: str, _history, language: str) -> str:
    language = language if language in UI_TEXT else "English"
    text = UI_TEXT[language]
    sector = (message or "").strip()
    if not sector:
        return text["greeting"]
    try:
        result = StockPicker(llm=fallback_llm()).crew().kickoff(inputs={
            "sector": sector,
            "current_date": date.today().isoformat(),
            "language_instruction": text["instruction"],
        })
    except Exception as error:
        print(f"[web] stock analysis failed ({type(error).__name__})", flush=True)
        return text["error"]
    return result.raw


def submit_sector(message: str, history: list[dict], language: str):
    """Render the user turn before the queued research starts."""
    message = (message or "").strip()
    if not message:
        raise gr.Error("Ingresá un sector." if language == "Español" else "Enter a sector.")
    status = "Analizando el sector y evaluando empresas para seleccionar una candidata…" if language == "Español" else "Analyzing the sector and evaluating companies to select a candidate…"
    return gr.Textbox(value="", interactive=False), [
        *(history or []),
        {"role": "user", "content": message},
        {"role": "assistant", "content": status},
    ], gr.Button(interactive=False)


def finish_submission(history: list[dict], language: str):
    if len(history) < 2 or history[-2]["role"] != "user":
        return gr.Textbox(interactive=True), history, gr.Button(interactive=True)
    content = history[-2]["content"]
    # Gradio 6 normalizes Chatbot input into typed content blocks.
    message = content if isinstance(content, str) else "\n".join(
        block["text"] for block in content if block.get("type") == "text"
    )
    response = analyze_sector(message, history[:-2], language)
    return gr.Textbox(interactive=True), [
        *history[:-1],
        {"role": "assistant", "content": response},
    ], gr.Button(interactive=True)


def submit_english(message: str, history: list[dict]):
    return submit_sector(message, history, "English")


def submit_spanish(message: str, history: list[dict]):
    return submit_sector(message, history, "Español")


def finish_english(history: list[dict]):
    return finish_submission(history, "English")


def finish_spanish(history: list[dict]):
    return finish_submission(history, "Español")


initial = UI_TEXT["English"]
with gr.Blocks(delete_cache=(3600, 86400)) as demo:
    with gr.Row(elem_id="title-row"):
        with gr.Column(scale=1, min_width=0, elem_id="header-copy"):
            header = gr.HTML(header_html("English"), elem_id="stock-header")
        with gr.Column(scale=0, min_width=180, elem_id="language-control"):
            gr.Markdown("Idioma / Language:", elem_id="language-label")
            language = gr.Dropdown(
                choices=["Español", "English"], value="English", show_label=False,
                container=False, interactive=True, elem_id="language-selector",
            )

    with gr.Group(visible=True) as english_chat:
        english_chatbot = gr.Chatbot(
            value=[{"role": "assistant", "content": initial["greeting"]}],
            show_label=False, height=520, elem_id="stock-chat-en",
        )
        english_report, english_download = download_controls("English")
        gr.Markdown(initial["examples"], elem_classes="sector-examples-label")
        with gr.Row(elem_id="sector-examples-en", elem_classes="sector-examples"):
            english_buttons = [gr.Button(sector) for sector in SUGGESTED_SECTORS]
        with gr.Row(elem_id="sector-input-row-en", elem_classes="sector-input-row"):
            english_textbox = gr.Textbox(
                placeholder=initial["placeholder"], show_label=False, container=False,
                scale=1, elem_id="sector-input-en",
            )
            english_submit = gr.Button(initial["submit"], variant="primary", scale=0)
        for button, sector in zip(english_buttons, SUGGESTED_SECTORS):
            button.click(lambda value=sector: value, outputs=english_textbox)
        english_submit.click(
            prepare_with_downloads(submit_english), [english_textbox, english_chatbot],
            [english_textbox, english_chatbot, english_submit, english_report, english_download], queue=False,
        ).success(
            finish_with_downloads(finish_english, UI_TEXT["English"]["error"]), english_chatbot,
            [english_textbox, english_chatbot, english_submit, english_report, english_download], show_progress="hidden",
        )
        english_textbox.submit(
            prepare_with_downloads(submit_english), [english_textbox, english_chatbot],
            [english_textbox, english_chatbot, english_submit, english_report, english_download], queue=False,
        ).success(
            finish_with_downloads(finish_english, UI_TEXT["English"]["error"]), english_chatbot,
            [english_textbox, english_chatbot, english_submit, english_report, english_download], show_progress="hidden",
        )

    with gr.Group(visible=False) as spanish_chat:
        spanish = UI_TEXT["Español"]
        spanish_chatbot = gr.Chatbot(
            value=[{"role": "assistant", "content": spanish["greeting"]}],
            show_label=False, height=520, elem_id="stock-chat-es",
        )
        spanish_report, spanish_download = download_controls("Español")
        gr.Markdown(spanish["examples"], elem_classes="sector-examples-label")
        with gr.Row(elem_id="sector-examples-es", elem_classes="sector-examples"):
            spanish_buttons = [gr.Button(SPANISH_SECTOR_LABELS[sector]) for sector in SUGGESTED_SECTORS]
        with gr.Row(elem_id="sector-input-row-es", elem_classes="sector-input-row"):
            spanish_textbox = gr.Textbox(
                placeholder=spanish["placeholder"], show_label=False, container=False,
                scale=1, elem_id="sector-input-es",
            )
            spanish_submit = gr.Button(spanish["submit"], variant="primary", scale=0)
        for button, sector in zip(spanish_buttons, SUGGESTED_SECTORS):
            button.click(lambda value=sector: value, outputs=spanish_textbox)
        spanish_submit.click(
            prepare_with_downloads(submit_spanish), [spanish_textbox, spanish_chatbot],
            [spanish_textbox, spanish_chatbot, spanish_submit, spanish_report, spanish_download], queue=False,
        ).success(
            finish_with_downloads(finish_spanish, UI_TEXT["Español"]["error"]), spanish_chatbot,
            [spanish_textbox, spanish_chatbot, spanish_submit, spanish_report, spanish_download], show_progress="hidden",
        )
        spanish_textbox.submit(
            prepare_with_downloads(submit_spanish), [spanish_textbox, spanish_chatbot],
            [spanish_textbox, spanish_chatbot, spanish_submit, spanish_report, spanish_download], queue=False,
        ).success(
            finish_with_downloads(finish_spanish, UI_TEXT["Español"]["error"]), spanish_chatbot,
            [spanish_textbox, spanish_chatbot, spanish_submit, spanish_report, spanish_download], show_progress="hidden",
        )

    language.change(
        localized_ui, inputs=language, outputs=[header, english_chat, spanish_chat],
        js="(language) => { document.title = language === 'Español' ? 'Selector de acciones' : 'Stock Picker'; return language; }",
    )
    browser_language = gr.Textbox(visible=False)
    demo.load(
        initialize_language, inputs=browser_language, outputs=[language, header, english_chat, spanish_chat],
        js="() => navigator.language || ''",
    )

demo.queue(default_concurrency_limit=1)

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=int(os.getenv("PORT", "7860")),
        css=CSS,
        js=JS,
        theme=gr.themes.Base(),
    )
