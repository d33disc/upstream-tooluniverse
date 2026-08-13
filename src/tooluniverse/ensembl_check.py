import re

def ensembl_gene_is_valid(value: str) -> bool:
    return bool(re.match(r'^ENSG\d{11}$', value))

if __name__ == '__main__':
    # Test cases
    assert ensembl_gene_is_valid('ENSG00000141510')  # True
    assert not ensembl_gene_is_valid('ENSG123')     # False (too short)
    assert not ensembl_gene_is_valid('ENST00000269305')  # False (ENST)
    assert not ensembl_gene_is_valid('abc')        # False (not ENSG)
    print('PASS')
