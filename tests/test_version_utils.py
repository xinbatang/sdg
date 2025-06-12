import pytest
from main_functions import compare_versions

@pytest.mark.parametrize("a,b,expected", [
    ("00A", "00A", 0),
    ("01A", "00A", 1),
    ("00B", "00A", 1),
    ("00A", "00B", -1),
    ("01", "01A", -1),
    ("01B", "01", 1),
    ("01B", "01B", 0),
    ("1A", "1B", -1),
    ("2", "1", 1),
    ("", "1", -1),
    ("1", "", 1),
])
def test_compare_versions(a, b, expected):
    result = compare_versions(a, b)
    if expected == 0:
        assert result == 0
    elif expected > 0:
        assert result > 0
    else:
        assert result < 0

def test_compare_versions_invalid_input():
    try:
        compare_versions("??", "!!")
    except Exception:
        pytest.fail("compare_versions should not raise exception on invalid input")