import unittest
import utils


class TestUtils(unittest.TestCase):
    def test_username_valid_only_char(self):
        self.assertTrue(utils.is_username_valid("meunomeejulia"))

    def test_username_valid_with_hyphen_and_number(self):
        self.assertTrue(utils.is_username_valid("meunomee-julia99"))

    def test_username_valid_upper_case(self):
        self.assertTrue(utils.is_username_valid("MeuNomeEJulia99"))

    def test_username_invalid_underscore(self):
        self.assertFalse(utils.is_username_valid("MeuNome_Julia99"))

    def test_username_invalid_space(self):
        self.assertFalse(utils.is_username_valid("Issodai Talkey"))