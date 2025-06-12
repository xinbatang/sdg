import pytest
import os

from pathlib import Path
from main_functions import extract_major_version, compare_versions,extract_wm_versions

def find_latest_iso_local(iso_dir: str, line_id: str):
    """
    在本地 ISO 目录中查找 line_id 对应的最新 ISO 文件
    """
    best_file = ""
    best_version = ""

    for file in Path(iso_dir).glob(f"{line_id}*.pdf"):
        fname = file.name
        version = extract_major_version(fname, mode='iso')
        if not version:
            continue
        if not best_version or compare_versions(version, best_version) > 0:
            best_version = version
            best_file = fname

    return best_file, best_version

def find_latest_wm_local(wm_dir: str, line_id: str):
    """
    在本地 WM 目录中查找 line_id 对应的最新 WM 文件
    优先比较主版本，相同主版本时比较子版本
    """
    best_file = ""
    best_main = ""
    best_sub = ""

    for file in Path(wm_dir).glob(f"{line_id}*.pdf"):
        fname = file.name
        main_ver, sub_ver = extract_wm_versions(fname)
        if not main_ver:
            continue
        if (not best_main or compare_versions(main_ver, best_main) > 0 or
            (compare_versions(main_ver, best_main) == 0 and compare_versions(sub_ver, best_sub) > 0)):
            best_file = fname
            best_main = main_ver
            best_sub = sub_ver

    return best_file, best_main

# 辅助函数：创建假 PDF
@pytest.fixture
def make_pdf(tmp_path):
    def _make(fname):
        path = tmp_path / fname
        path.write_text("fake content")
        return path
    return _make

@pytest.fixture
def make_pdf():
    def _make(path):
        path.write_text("dummy content")
    return _make

def test_find_latest_iso_local_simple(tmp_path, make_pdf):
    pdfs = [
        "PIPE-001_01A.pdf",
        "PIPE-001_02B.pdf",
        "PIPE-001_01B.pdf"
    ]
    for name in pdfs:
        make_pdf(tmp_path / name)
    fname, version = find_latest_iso_local(str(tmp_path), "PIPE-001")
    assert version == "02B"

def test_find_latest_iso_local_with_review(tmp_path, make_pdf):
    make_pdf(tmp_path / "PIPE-001_01A_REVIEW.pdf")
    make_pdf(tmp_path / "PIPE-001_01B.pdf")
    fname, version = find_latest_iso_local(str(tmp_path), "PIPE-001")
    assert version == "01B"

def test_find_latest_iso_local_no_match(tmp_path, make_pdf):
    make_pdf(tmp_path / "SOME-OTHER-FILE.pdf")
    fname, version = find_latest_iso_local(str(tmp_path), "PIPE-001")
    assert fname == ""
    assert version == ""

def test_find_latest_wm_local(tmp_path, make_pdf):
    files = [
        "PIPE-001_Rev01A_04S.pdf",
        "PIPE-001_Rev02B_05S.pdf",
        "PIPE-001_Rev01B_03S.pdf"
    ]
    for fname in files:
        make_pdf(tmp_path / fname)
    fname, version = find_latest_wm_local(str(tmp_path), "PIPE-001")
    assert version == "02B"

def test_find_latest_wm_review_and_case(tmp_path, make_pdf):
    make_pdf(tmp_path / "PIPE-001_Rev01B_REVIEW.pdf")
    make_pdf(tmp_path / "PIPE-001_Rev01C.pdf")
    fname, version = find_latest_wm_local(str(tmp_path), "PIPE-001")
    assert version == "01C"

def test_find_latest_wm_no_match(tmp_path, make_pdf):
    make_pdf(tmp_path / "OTHER.pdf")
    fname, version = find_latest_wm_local(str(tmp_path), "PIPE-001")
    assert fname == ""
    assert version == ""


def test_find_latest_wm_with_subversion(tmp_path):
    from main_functions import find_latest_wm

    files = [
        "PIPE-002_Rev00A_00.pdf",
        "PIPE-002_Rev00A_01.pdf",
        "PIPE-002_Rev00B_00.pdf",
    ]
    for name in files:
        with open(tmp_path / name, 'wb') as f:
            f.write(b"%PDF-1.4 mock")

    from main_functions import everything_search
    def mock_search(dir, line_id):
        return [str(tmp_path / name) for name in os.listdir(tmp_path) if line_id in name]

    # patch everything_search
    import main_functions
    main_functions.everything_search = mock_search

    fname, ver = find_latest_wm(str(tmp_path), "PIPE-002")
    assert ver == "00B_00"
    assert "Rev00B" in fname

