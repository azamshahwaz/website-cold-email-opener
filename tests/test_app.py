from pathlib import Path

import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest

from modules.demo import DEMO_LABEL

APP_PATH = Path(__file__).resolve().parent.parent / "app.py"


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "")
    st.cache_resource.clear()


def new_app() -> AppTest:
    return AppTest.from_file(str(APP_PATH), default_timeout=20)


def all_markdown(at: AppTest) -> str:
    return "\n".join(m.value for m in at.markdown)


def test_app_starts_in_demo_mode_without_api_key():
    at = new_app().run()
    assert not at.exception
    assert at.session_state["demo_mode"] is True
    assert "Website to AI Cold Email Opener" in all_markdown(at)
    assert "Generate personalized, website-grounded three-line openers" in all_markdown(at)


def test_demo_generation_shows_label_and_three_lines():
    at = new_app().run()
    at.button(key="generate_btn").click().run()
    assert not at.exception and not at.error
    text = all_markdown(at)
    assert DEMO_LABEL in text
    assert text.count('class="opener-line"') == 3
    assert "Company Website" in text and "Company Description" in text
    assert any(b.key == "again_btn" for b in at.button) and any(b.key == "clear_btn" for b in at.button)


def test_clear_button_resets_result():
    at = new_app().run()
    at.button(key="generate_btn").click().run()
    at.button(key="clear_btn").click().run()
    assert at.session_state["result"] is None
    assert 'class="opener-line"' not in all_markdown(at)


def test_live_mode_without_key_shows_clear_error():
    at = new_app()
    at.session_state["demo_mode"] = False
    at.run()
    at.text_input(key="url_input").set_value("https://example.com").run()
    at.button(key="generate_btn").click().run()
    assert not at.exception
    assert any("GEMINI_API_KEY" in e.value for e in at.error)


def test_live_mode_invalid_url_shows_error(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "x" * 20)
    st.cache_resource.clear()
    at = new_app()
    at.session_state["demo_mode"] = False
    at.run()
    at.text_input(key="url_input").set_value("http://localhost:80/admin").run()
    at.button(key="generate_btn").click().run()
    assert not at.exception
    assert at.error and "private or internal" in at.error[0].value


def test_live_mode_empty_url_shows_error(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "x" * 20)
    st.cache_resource.clear()
    at = new_app()
    at.session_state["demo_mode"] = False
    at.run()
    at.button(key="generate_btn").click().run()
    assert at.error and "enter a website URL" in at.error[0].value
