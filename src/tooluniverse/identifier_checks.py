"""CAS Registry Number validation."""


def cas_is_valid(value: str) -> bool:
    """Validate a CAS Registry Number by its check digit.

    Format: XXXXX-YY-Z where:
      - First block (XXXXX): 2 to 7 digits
      - Middle block (YY): exactly 2 digits
      - Check digit (Z): single digit, equals weighted sum of all preceding digits mod 10
    
    Weights are assigned right-to-left starting at 1 for the last digit before check.
    
    Returns True if valid, False otherwise.
    """
    # Must match pattern: first block (2-7 digits), dash, middle block (exactly 2 digits), dash, check digit (1 digit)
    import re
    
    pattern = r'^(\d{2,7})-(\d{2})-(\d)$'
    match = re.match(pattern, value)
    
    if not match:
        return False
    
    first_block = match.group(1)
    middle_block = match.group(2)
    check_digit_str = match.group(3)
    
    # Combine all digits before the check digit (first block + middle block)
    all_digits_before_check = first_block + middle_block
    
    if not all_digits_before_check.isdigit():
        return False
    
    # Calculate weighted sum: read right-to-left with weights 1, 2, 3, ...
    total = 0
    weight = 1
    for digit_char in reversed(all_digits_before_check):
        digit = int(digit_char)
        total += digit * weight
        weight += 1
    
    expected_check_digit = str(total % 10)
    
    return check_digit_str == expected_check_digit


if __name__ == '__main__':
    # Test cases that should be True
    assert cas_is_valid('50-78-2'), "Failed: '50-78-2'"
    assert cas_is_valid('7732-18-5'), "Failed: '7732-18-5'"
    assert cas_is_valid('58-08-2'), "Failed: '58-08-2'"
    assert cas_is_valid('134523-00-5'), "Failed: '134523-00-5'"
    
    # Test cases that should be False
    assert not cas_is_valid('5O-78-2'), "Failed: '5O-78-2' (letter O instead of 0)"
    assert not cas_is_valid('50-780-2'), "Failed: '50-780-2' (three-digit middle block)"
    assert not cas_is_valid('abc'), "Failed: 'abc'"
    
    print('PASS')
