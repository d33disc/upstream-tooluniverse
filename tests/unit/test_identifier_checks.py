"""Tests for tooluniverse.identifier_checks."""

import pytest

from tooluniverse.identifier_checks import cas_is_valid, inchikey_is_valid


@pytest.mark.parametrize(
    "value",
    [
        "50-78-2",
        "7732-18-5",
        "58-08-2",
        "134523-00-5",
    ],  # aspirin, water, caffeine, atorvastatin
)
def test_cas_accepts_real_numbers(value):
    assert cas_is_valid(value)


@pytest.mark.parametrize(
    "value",
    [
        "5O-78-2",  # OCR: letter O instead of zero
        "50-780-2",  # three-digit middle block
        "50-7-2",  # one-digit middle block
        "5-78-2",  # one-digit first block
        "50-78-3",  # wrong check digit
        "abc",
        "",
    ],
)
def test_cas_rejects_malformed(value):
    assert not cas_is_valid(value)


def test_inchikey_accepts_real():
    assert inchikey_is_valid("BSYNRYMUTXBXSQ-UHFFFAOYSA-N")  # aspirin


@pytest.mark.parametrize(
    "value",
    [
        "abc",
        "bsynrymutxbxsq-uhfffaosa-n",  # lowercase
        "BSYNRYMUTXBXS-UHFFFAOYSA-N",  # 13-letter first block
        "BSYNRYMUTXBXSQ-UHFFFAOYSA-NN",  # 2-letter suffix
    ],
)
def test_inchikey_rejects_malformed(value):
    assert not inchikey_is_valid(value)
