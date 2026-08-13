import re

def hgnc_is_valid(value: str) -> bool:
    """Check if value is a valid HGNC ID: 'HGNC:' followed by one or more digits."""
    return re.match(r'^HGNC:\d+$', value) is not None

if __name__ == '__main__':
    # Test cases
    assert hgnc_is_valid('HGNC:11998')  # True
    assert hgnc_is_valid('HGNC:1100')   # True
    assert not hgnc_is_valid('HGNC:')  # False (no digits)
    assert not hgnc_is_valid('hgnc:11998')  # False (lowercase)
    assert not hgnc_is_valid('abc')  # False
    print('PASS')
