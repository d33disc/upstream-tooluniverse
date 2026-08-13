import re

def mondo_is_valid(value: str) -> bool:
    pattern = r'^MONDO:\d{7}$'
    return bool(re.match(pattern, value))

if __name__ == '__main__':
    assert mondo_is_valid('MONDO:0005148')
    assert not mondo_is_valid('MONDO:123')
    assert not mondo_is_valid('MONDO0005148')
    assert not mondo_is_valid('abc')
    print('PASS')

