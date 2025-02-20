import json
import yaml
import sqlite3
import typer
import re
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.progress import track
from db import init_db, insert_record, fetch_records
from logger import get_logger

app = typer.Typer()
console = Console()
logger = get_logger()

CONFIG_PATH = Path(__file__).parent / "config.yaml"

DEFAULT_CONFIG = {
    "profiles": {
        "default": {
            "appearance": {
                "theme": "dark",
                "logo": "🕊️ Confessor Notebook 🕊️"
            },
            "templates": {
                "report": "[bold green]{title}[/bold green]\n{content}"
            },
            "en": {
                "confession": [
                    "How was your day?",
                    "What did you achieve today?",
                    "What challenges did you face today?"
                ],
                "meditation": [
                    "How do you feel today?",
                    "What are you grateful for today?",
                    "What thoughts are on your mind?"
                ]
            },
            "ru": {
                "confession": [
                    "Как прошел твой день?",
                    "Что ты успел сделать сегодня?",
                    "С какими трудностями ты столкнулся сегодня?"
                ],
                "meditation": [
                    "Как ты себя чувствуешь сегодня?",
                    "За что ты сегодня благодарен?",
                    "О чем ты думаешь?"
                ]
            }
        }
    }
}


def ensure_config():
    if not CONFIG_PATH.exists():
        with CONFIG_PATH.open("w", encoding="utf-8") as f:
            yaml.dump(DEFAULT_CONFIG, f, allow_unicode=True)


def load_config(profile: str = "default") -> dict:
    ensure_config()
    try:
        with CONFIG_PATH.open("r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        return config.get("profiles", {}).get(profile, DEFAULT_CONFIG["profiles"]["default"])
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return DEFAULT_CONFIG["profiles"]["default"]


def save_config(config_data: dict, profile: str = "default"):
    try:
        with CONFIG_PATH.open("w", encoding="utf-8") as f:
            yaml.dump({"profiles": {profile: config_data}},
                      f, allow_unicode=True)
    except Exception as e:
        logger.error(f"Error saving config: {e}")


def validate_answer(question: str, answer: str) -> bool:
    if "date" in question.lower():
        pattern = r"\d{4}-\d{2}-\d{2}"
        if not re.search(pattern, answer):
            return False
    if "number" in question.lower() or "число" in question.lower():
        if not answer.isdigit():
            return False
    return True


def ask_questions(questions: list) -> dict:
    answers = {}
    for question in questions:
        valid = False
        while not valid:
            answer = Prompt.ask(f"[bold blue]{question}[/bold blue]")
            if validate_answer(question, answer):
                valid = True
            else:
                console.print(
                    Panel("Invalid format. Please try again.", style="red"))
        answers[question] = answer
    return answers


def build_report(record: dict, lang: str, template: str) -> str:
    title = "Daily Report" if lang == "en" else "Отчет за день"
    content = ""
    for question, answer in record.items():
        content += f"[bold yellow]{question}[/bold yellow]\n{answer}\n\n"
    return template.format(title=title, content=content)


def display_logo(logo: str):
    console.print(Panel(logo, style="bold magenta"))


@app.command()
def run(
    mode: str = typer.Option("confession", "--mode",
                             "-m", help="Режим: meditation или confession"),
    lang: str = typer.Option("en", "--lang", "-l", help="Язык: en или ru"),
    profile: str = typer.Option(
        "default", "--profile", "-p", help="Профиль пользователя")
):
    init_db()
    config = load_config(profile)
    logo = config.get("appearance", {}).get("logo", "Confessor Notebook")
    display_logo(logo)
    welcome = "Welcome to Confessor Notebook. Answer the questions below." if lang == "en" else "Добро пожаловать в Исповедник. Ответьте на следующие вопросы."
    console.print(Panel(welcome, style="cyan"))
    questions = config.get(lang, {}).get(mode, [])
    if not questions:
        msg = f"No questions for mode '{mode}' and language '{lang}' in profile '{profile}'." if lang == "en" else f"Нет вопросов для режима '{mode}' и языка '{lang}' в профиле '{profile}'."
        console.print(Panel(msg, style="red"))
        raise typer.Exit()
    answers = ask_questions(questions)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    record = {"profile": profile, "mode": mode, "lang": lang,
              "timestamp": timestamp, "answers": json.dumps(answers, ensure_ascii=False)}
    with console.status("Saving record...", spinner="dots"):
        for _ in track(range(10), description="Processing..."):
            pass
        insert_record(record)
    template = config.get("templates", {}).get(
        "report", "[bold green]{title}[/bold green]\n{content}")
    report_text = build_report(answers, lang, template)
    console.print(Panel(report_text, title="Report" if lang ==
                  "en" else "Отчет", style="green"))


@app.command()
def report(
    week: bool = typer.Option(False, "--week", "-w",
                              help="Сформировать отчёт за неделю"),
    lang: str = typer.Option("en", "--lang", "-l", help="Язык: en или ru"),
    profile: str = typer.Option(
        "default", "--profile", "-p", help="Профиль пользователя")
):
    init_db()
    records = fetch_records(profile, lang)
    if not records:
        msg = "No records found." if lang == "en" else "Записей не найдено."
        console.print(Panel(msg, style="red"))
        raise typer.Exit()
    if week:
        title = "Weekly Report" if lang == "en" else "Отчет за неделю"
        table = Table(title=title)
        table.add_column("Date", style="cyan", no_wrap=True)
        table.add_column("Mode", style="magenta")
        table.add_column("Summary", style="yellow")
        for rec in records:
            summary = " | ".join(
                [f"{k}: {v}" for k, v in json.loads(rec["answers"]).items()][:2])
            table.add_row(rec["timestamp"], rec["mode"], summary)
        console.print(table)
    else:
        config = load_config(profile)
        template = config.get("templates", {}).get(
            "report", "[bold green]{title}[/bold green]\n{content}")
        for rec in records:
            answers = json.loads(rec["answers"])
            report_text = build_report(answers, lang, template)
            console.print(
                Panel(report_text, title="Report" if lang == "en" else "Отчет", style="green"))


@app.command()
def add_question(
    lang: str = typer.Option("en", "--lang", "-l", help="Язык: en или ru"),
    mode: str = typer.Option("confession", "--mode",
                             "-m", help="Режим: meditation или confession"),
    profile: str = typer.Option(
        "default", "--profile", "-p", help="Профиль пользователя"),
    question: str = typer.Argument(..., help="Новый вопрос для добавления")
):
    config = load_config(profile)
    questions = config.get(lang, {}).get(mode, [])
    questions.append(question)
    config[lang][mode] = questions
    save_config(config, profile)
    msg = "Question added." if lang == "en" else "Вопрос добавлен."
    console.print(Panel(msg, style="green"))


@app.command()
def list_questions(
    lang: str = typer.Option("en", "--lang", "-l", help="Язык: en или ru"),
    mode: str = typer.Option("confession", "--mode",
                             "-m", help="Режим: meditation или confession"),
    profile: str = typer.Option(
        "default", "--profile", "-p", help="Профиль пользователя")
):
    config = load_config(profile)
    questions = config.get(lang, {}).get(mode, [])
    if not questions:
        msg = "No questions found." if lang == "en" else "Вопросы не найдены."
        console.print(Panel(msg, style="red"))
    else:
        title = "Questions" if lang == "en" else "Вопросы"
        console.print(Panel("\n".join(questions), title=title, style="blue"))


@app.command()
def add_profile(
    profile: str = typer.Argument(..., help="Название нового профиля")
):
    config_all = {}
    if CONFIG_PATH.exists():
        with CONFIG_PATH.open("r", encoding="utf-8") as f:
            config_all = yaml.safe_load(f)
    profiles = config_all.get("profiles", {})
    if profile in profiles:
        console.print(Panel("Profile already exists.", style="red"))
        raise typer.Exit()
    profiles[profile] = DEFAULT_CONFIG["profiles"]["default"]
    with CONFIG_PATH.open("w", encoding="utf-8") as f:
        yaml.dump({"profiles": profiles}, f, allow_unicode=True)
    console.print(Panel(f"Profile '{profile}' added.", style="green"))


@app.command()
def remove_profile(
    profile: str = typer.Argument(..., help="Название профиля для удаления")
):
    if not CONFIG_PATH.exists():
        console.print(Panel("No config found.", style="red"))
        raise typer.Exit()
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        config_all = yaml.safe_load(f)
    profiles = config_all.get("profiles", {})
    if profile not in profiles:
        console.print(Panel("Profile not found.", style="red"))
        raise typer.Exit()
    del profiles[profile]
    with CONFIG_PATH.open("w", encoding="utf-8") as f:
        yaml.dump({"profiles": profiles}, f, allow_unicode=True)
    console.print(Panel(f"Profile '{profile}' removed.", style="green"))


@app.command()
def sync():
    console.print(
        Panel("Cloud synchronization is not implemented yet.", style="yellow"))


if __name__ == "__main__":
    app()
