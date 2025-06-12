from tkinter import messagebox
from pypdf import PdfReader, PdfWriter

def is_pdf_valid(filepath):
    try:
        reader = PdfReader(filepath)
        # 试着访问第一页
        _ = reader.pages[0]
        return True
    except Exception:
        return False

def merge_pdf_files(files, outname):
    writer = PdfWriter()
    bad_files = []
    for f in files:
        if not is_pdf_valid(f):
            bad_files.append(f)
            continue
        try:
            reader = PdfReader(f)
            for page in reader.pages:
                writer.add_page(page)
        except Exception as e:
            bad_files.append(f"{f} (合并时出错: {e})")
    with open(outname, "wb") as fout:
        writer.write(fout)
    return bad_files  # 合并后返回损坏文件列表

