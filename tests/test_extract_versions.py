import pytest
from main_functions import extract_major_version, extract_wm_versions

@pytest.mark.parametrize("filename, mode, expected", [
    ("PA-201-0107-A-12-1.pdf", "iso", "1"),
    ("CWS-212-0591-A-01.pdf", "iso", ""),  # 5段结构，返回空字符串
    ("AV-204-0260-A-01_01A.pdf", "iso", "01A")
])
def test_extract_major_version(filename, mode, expected):
    assert extract_major_version(filename, mode) == expected

@pytest.mark.parametrize("filename, expected_main, expected_sub", [
    ("PIPE-001_Rev01A_04S.pdf", "01A", "04S"),
    ("PIPE-001_Rev02B.pdf", "02B", ""),
    ("PIPE-001_02S.pdf", "", "02S"),
    ("PIPE-001.pdf", "", "")
])
def test_extract_wm_versions(filename, expected_main, expected_sub):
    main_ver, sub_ver = extract_wm_versions(filename)
    assert main_ver == expected_main
    assert sub_ver == expected_sub
