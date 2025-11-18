import pytest
from pipeline.utils import validate_transcript, format_transcript

def test_empty_transcript():
    valid, err = validate_transcript({})
    assert not valid and "empty" in err.lower()

def test_too_short_transcript():
    valid, err = validate_transcript({"interviewer": "Hi"})
    assert not valid and "at least 2 exchanges" in err.lower()

def test_missing_candidate():
    valid, err = validate_transcript({"interviewer": "Q1", "interviewer_1": "Q2"})
    assert not valid and "candidate" in err.lower()

def test_valid_transcript():
    transcript = {"interviewer": "Q1", "candidate": "A1"}
    valid, err = validate_transcript(transcript)
    assert valid and err is None

def test_formatting_order():
    transcript = {
        "candidate": "answer",
        "interviewer": "question",
        "candidate_1": "answer 2",
        "interviewer_1": "question 2"
    }
    formatted = format_transcript(transcript)
    assert formatted.index("Interviewer: question") < formatted.index("Candidate: answer")
