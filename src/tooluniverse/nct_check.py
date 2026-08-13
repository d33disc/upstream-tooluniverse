import re

def nct_is_valid(value: str) -> bool:
    """Check if value is a valid ClinicalTrials.gov NCT number: NCT followed by exactly 8 digits."""
    pattern = r'^NCT\d{8}$'
    return bool(re.match(pattern, value))

if __name__ == '__main__':
    # Test cases
    assert nct_is_valid('NCT01158625')  # Valid NCT number
    assert not nct_is_valid('NCT123')     # Too short
    assert not nct_is_valid('nct01158625') # Wrong case
    assert not nct_is_valid('abc')        # Invalid
    print('PASS')
