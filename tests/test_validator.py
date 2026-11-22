import pytest

from modules.errors import InvalidOutputError
from modules.validator import clean_opener_text, validate_opener

L1 = "Acme Routes plans daily delivery routes for independent bakeries and cafes."
L2 = "Your site stresses that fresh bread has a short shelf life, so late deliveries cost real money."
L3 = "When a van is running late, who decides which customer gets their order first today?"


def test_exactly_three_valid_lines():
    assert validate_opener(f"{L1}\n{L2}\n{L3}") == [L1, L2, L3]


def test_blank_lines_between_lines_are_ignored():
    assert validate_opener(f"{L1}\n\n{L2}\n\n{L3}\n") == [L1, L2, L3]


def test_two_lines_rejected():
    with pytest.raises(InvalidOutputError):
        validate_opener(f"{L1}\n{L2}")


def test_four_lines_rejected():
    with pytest.raises(InvalidOutputError):
        validate_opener(f"{L1}\n{L2}\n{L3}\nThis is an extra fourth line of text.")


@pytest.mark.parametrize("raw", ["", "   \n\n  ", None])
def test_empty_output_rejected(raw):
    with pytest.raises(InvalidOutputError):
        validate_opener(raw)


def test_markdown_and_numbering_removed():
    raw = f"1. **{L1}**\n2) *{L2}*\n- `{L3}`"
    assert validate_opener(raw) == [L1, L2, L3]


def test_code_fence_labels_and_quotes_removed():
    raw = f"```text\nLine 1: {L1}\nLine 2: \"{L2}\"\nLine 3: {L3}\n```"
    assert validate_opener(raw) == [L1, L2, L3]


def test_excessively_long_output_rejected():
    with pytest.raises(InvalidOutputError):
        validate_opener(f"{L1}\n{L2}\n{'word ' * 80}")


def test_total_length_limit():
    long_line = "a" * 270
    with pytest.raises(InvalidOutputError):
        validate_opener(f"{long_line}\n{long_line}\n{long_line}")


def test_too_short_line_rejected():
    with pytest.raises(InvalidOutputError):
        validate_opener(f"{L1}\nOk.\n{L3}")


@pytest.mark.parametrize("bad", ["Hi there, I hope you are doing well today.", "Subject: Quick question for you",
                                 "Best regards, the sales team of Acme"])
def test_greetings_and_signatures_rejected(bad):
    with pytest.raises(InvalidOutputError):
        validate_opener(f"{bad}\n{L2}\n{L3}")


def test_generic_cliche_rejected():
    with pytest.raises(InvalidOutputError):
        validate_opener(f"{L1}\n{L2}\nI came across your website and I was curious about routing.")


def test_clean_keeps_inner_asterisks_and_numbers():
    assert clean_opener_text("Revenue grew 3 * 4 times in 2024 for this company") == \
        ["Revenue grew 3 * 4 times in 2024 for this company"]
