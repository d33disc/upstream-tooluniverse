"""Unit tests for the identifier format validators (schema-teeth pilot, fleet-generated)."""

from tooluniverse.ensembl_check import ensembl_gene_is_valid
from tooluniverse.hgnc_check import hgnc_is_valid
from tooluniverse.identifier_checks import cas_is_valid
from tooluniverse.inchikey_check import inchikey_is_valid
from tooluniverse.mondo_check import mondo_is_valid
from tooluniverse.nct_check import nct_is_valid


class TestCAS:
    def test_valid(self):
        assert cas_is_valid('50-78-2')
        assert cas_is_valid('7732-18-5')
        assert cas_is_valid('58-08-2')
        assert cas_is_valid('134523-00-5')

    def test_invalid(self):
        assert not cas_is_valid('5O-78-2')   # letter O instead of 0
        assert not cas_is_valid('50-780-2')  # three-digit middle block
        assert not cas_is_valid('50-78-3')   # wrong check digit
        assert not cas_is_valid('abc')


class TestEnsembl:
    def test_valid(self):
        assert ensembl_gene_is_valid('ENSG00000141510')

    def test_invalid(self):
        assert not ensembl_gene_is_valid('ENSG123')
        assert not ensembl_gene_is_valid('ENST00000269305')
        assert not ensembl_gene_is_valid('abc')


class TestHGNC:
    def test_valid(self):
        assert hgnc_is_valid('HGNC:11998')
        assert hgnc_is_valid('HGNC:1100')

    def test_invalid(self):
        assert not hgnc_is_valid('HGNC:')
        assert not hgnc_is_valid('hgnc:11998')
        assert not hgnc_is_valid('abc')


class TestInChIKey:
    def test_valid(self):
        assert inchikey_is_valid('BSYNRYMUTXBXSQ-UHFFFAOYSA-N')

    def test_invalid(self):
        assert not inchikey_is_valid('abc')
        assert not inchikey_is_valid('bsynrymutxbxsq-uhfffaosa-n')


class TestMONDO:
    def test_valid(self):
        assert mondo_is_valid('MONDO:0005148')

    def test_invalid(self):
        assert not mondo_is_valid('MONDO:123')
        assert not mondo_is_valid('MONDO0005148')
        assert not mondo_is_valid('abc')


class TestNCT:
    def test_valid(self):
        assert nct_is_valid('NCT01158625')

    def test_invalid(self):
        assert not nct_is_valid('NCT123')
        assert not nct_is_valid('nct01158625')
        assert not nct_is_valid('abc')
