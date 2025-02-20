import os
import tempfile
import sqlite3
import json
from pathlib import Path
import pytest
from db import init_db, insert_record, fetch_records
from confessor-notebook import load_config, validate_answer, build_report


@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    temp_db = tmp_path / "test.db"
    monkeypatch.setattr("db.DB_PATH", temp_db)
    init_db()
    yield
    if temp_db.exists():
        temp_db.unlink()


def test_validate_answer_date():
    question = "Enter date (YYYY-MM-DD):"
    valid_answer = "2025-02-20"
    invalid_answer = "20/02/2025"
    assert validate_answer(question, valid_answer)
    assert not validate_answer(question, invalid_answer)


def test_validate_answer_number():
    question = "Enter number:"
    valid_answer = "123"
    invalid_answer = "abc"
    assert validate_answer(question, valid_answer)
    assert not validate_answer(question, invalid_answer)


def test_insert_and_fetch_record():
    record = {
        "profile": "default",
        "mode": "confession",
        "lang": "en",
        "timestamp": "2025-02-20 12:00:00",
        "answers": json.dumps({"Test question": "Test answer"})
    }
    insert_record(record)
    records = fetch_records("default", "en")
    assert len(records) == 1
    assert records[0]["profile"] == "default"


def test_build_report():
    answers = {"Q1": "A1", "Q2": "A2"}
    template = "[bold green]{title}[/bold green]\n{content}"
    report = build_report(answers, "en", template)
    assert "Daily Report" in report
    assert "Q1" in report
