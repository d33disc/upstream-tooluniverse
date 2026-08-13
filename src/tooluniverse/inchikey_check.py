import re

def inchikey_is_valid(value: str) -> bool:
    pattern = r'^[A-Z]{14}-[A-Z]{10}-[A-Z]$'
    return bool(re.match(pattern, value))

if __name__ == '__main__':
    assert inchikey_is_valid('BSYNRYMUTXBXSQ-UHFFFAOYSA-N')
    assert not inchikey_is_valid('abc')
    assert not inchikey_is_valid('bsynrymutxbxsq-uhfffaosa-n')
    print('PASS')
