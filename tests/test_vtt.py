from pathlib import Path

from content_lens.processors.vtt import parse_timestamp, parse_vtt


def test_parse_timestamp():
    assert parse_timestamp("00:01.500") == 1.5
    assert parse_timestamp("01:02:03.250") == 3723.25


def test_parse_vtt_fixture():
    turns = parse_vtt(Path("tests/fixtures/sample.vtt"))
    assert len(turns) == 3
    assert turns[0].text == "Hello & welcome"
    assert turns[2].text.endswith("speakers?")
