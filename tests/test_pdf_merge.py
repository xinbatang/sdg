import os
from pypdf import PdfWriter, PdfReader
from pdf_merge import merge_pdf_files

def make_fake_pdf(path, num_pages=1):
    writer = PdfWriter()
    for _ in range(num_pages):
        writer.add_blank_page(width=72, height=72)
    with open(path, "wb") as f:
        writer.write(f)

def test_merge_pdf_files(tmp_path):
    # 创建两个假 PDF 文件
    pdf1 = tmp_path / "file1.pdf"
    pdf2 = tmp_path / "file2.pdf"
    make_fake_pdf(pdf1, num_pages=1)
    make_fake_pdf(pdf2, num_pages=2)

    # 合并输出路径
    output = tmp_path / "merged.pdf"

    # 调用目标函数
    merge_pdf_files([str(pdf1), str(pdf2)], str(output))

    # 断言输出文件存在
    assert output.exists(), "合并后的 PDF 文件未创建"

    # 验证总页数
    reader = PdfReader(str(output))
    assert len(reader.pages) == 3, "合并后的 PDF 页数不正确，应为 3 页"
