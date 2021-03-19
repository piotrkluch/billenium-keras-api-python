import pytest
from contexts.prediction.domain.model.prediction import create_prediction


def test_prediction():
    p1 = create_prediction("Foo bar baz", "en-US")
    assert p1.phrase == "Foo bar baz"
    assert p1.language == "en-US"
    assert p1.language is not "de-DE"

    p2 = create_prediction("The brown fox jumped over the lazy dog", "en-EN")
    assert p2.phrase == "The brown fox jumped over the lazy dog"
    assert p2.language == "en-EN"
    assert p2.language is not "de-DE"

    assert p1 is not p2