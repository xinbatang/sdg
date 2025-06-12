from pypdf import PdfReader 
from pathlib import Path

# 文件所在目录
pdf_dir = Path(r"D:\myProject\真实场景\WM")
# 不带扩展名的目标文件名
target_name = "PA-204-0321-A-02_Rev01_02"

# 遍历目录，忽略大小写和后缀匹配
for f in pdf_dir.glob("*.*"):
    if f.stem.lower() == target_name.lower():
        log.info('"✅ 找到文件:: %s', f.name)
        try:
            reader = PdfReader(str(f))
            log.info("✅ PDF 打开成功")
            log.info('"页数：: %s', len(reader.pages))
        except Exception as e:
            log.error('"❌ 打开失败：: %s', e)
        break
else:
    log.info('"❌ 未找到匹配文件:: %s', target_name)
