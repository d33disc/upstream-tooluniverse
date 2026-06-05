"""Format and check-digit validation for biomedical/chemical identifiers.

These validators reject malformed or OCR-corrupted identifiers at the edge, so
downstream code can trust an identifier's shape instead of re-checking it. The
fixtures are real ToolUniverse identifiers (aspirin, water, atorvastatin, ...).
"""

import re

_CAS_RE = re.compile(r"^(\d{2,7})-(\d{2})-(\d)$")
_INCHIKEY_RE = re.compile(r"^[A-Z]{14}-[A-Z]{10}-[A-Z]$")


def cas_is_valid(value: str) -> bool:
    """Return True iff ``value`` is a valid CAS Registry Number.

    Format: 2-7 digits, ``-``, 2 digits, ``-``, 1 check digit. The check digit
    must equal the weighted sum of the preceding digits (read right-to-left with
    weights 1, 2, 3, ...) modulo 10 — which catches single-digit substitutions and
    transposition/OCR errors that a pure regex would accept (e.g. ``50-780-2``).
    """
    match = _CAS_RE.match(value)
    if not match:
        return False
    digits = match.group(1) + match.group(2)
    checksum = sum(i * int(d) for i, d in enumerate(reversed(digits), start=1)) % 10
    return checksum == int(match.group(3))


def inchikey_is_valid(value: str) -> bool:
    """Return True iff ``value`` matches the InChIKey format.

    An InChIKey is 14 uppercase letters, ``-``, 10 uppercase letters, ``-``, then
    a single uppercase letter (e.g. ``BSYNRYMUTXBXSQ-UHFFFAOYSA-N`` for aspirin).
    """
    return bool(_INCHIKEY_RE.match(value))
