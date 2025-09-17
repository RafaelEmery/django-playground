import pytest

from payments.utils import clean_document_number, is_valid_cnpj, is_valid_cpf


@pytest.mark.parametrize(
    "input_value, expected_output",
    [
        ("123.456.789-09", "12345678909"),
        ("12345678909", "12345678909"),
        ("123-456-789.09", "12345678909"),
        ("abc123def456ghi78909", "12345678909"),
        ("", ""),
        ("!!!", ""),
    ]
)
def test_clean_document_number(input_value, expected_output):
    assert clean_document_number(input_value) == expected_output


@pytest.mark.parametrize(
    "cpf, expected",
    [
        ("614.132.340-54", True),
        ("111.111.111-11", False),
        ("935.411.347-80", True),
        ("25212313040", True),
        ("000.000.000-00", False),
        ("935.411.347-81", False),
        ("935.411.347", False),
        ("935.411.347-800", False),
        ("abc935.411.347-80xyz", True),
        ("", False),
        ("!!!", False),
    ]
)
def test_is_valid_cpf(cpf, expected):
    assert is_valid_cpf(cpf) == expected


@pytest.mark.parametrize(
    "cnpj, expected",
    [
        ("82.975.730/0001-72", True),
        ("11.111.111/1111-11", False),
        ("00202657000131", True),
        ("00.000.000/0000-00", False),
        ("45.987.321/0001-11", False),
        ("45.987.321/0001", False),
        ("45.987.321/0001-100", False),
        ("abc45.987.321/0001-10xyz", False),
        ("", False),
        ("!!!", False),
    ]
)
def test_is_valid_cnpj(cnpj, expected):
    assert is_valid_cnpj(cnpj) == expected
