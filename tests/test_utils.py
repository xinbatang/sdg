import pytest

@pytest.mark.parametrize("ver, expected", [
    ("00A_00", "A"),
    ("01B_01S", "1B"),
    ("0", "0"),
    ("01", "1"),
    ("B", "B"),
    ("00B", "B"),
])
def test_normalize_ver(ver, expected):
    from utils import normalize_ver
    assert normalize_ver(ver) == expected

@pytest.mark.parametrize("a, b, expected", [
    ("00A_00", "00A_00", 0),
    ("00A_01", "00A_00", 1),
    ("00A_01", "00A_02", -1),
    ("00B_00", "00A_99", 1),
    ("01B_01S", "01B_01R", 1),
    ("01B_01", "01B", 1),       # b无子版本，a有 → a大
    ("01B", "01B_01", -1),      # a无子版本，b有 → b大
])
def test_compare_wm_versions(a, b, expected):
    from main_functions import compare_wm_versions
    assert compare_wm_versions(a, b) == expected

