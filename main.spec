# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

from PyInstaller.utils.hooks import collect_submodules

# 主程序路径
entry_script = 'src/main.py'

# 构建分析
a = Analysis(
    [entry_script],
    pathex=[],
    binaries=[],
    datas=[
        ('third_party/es.exe', '.'),  # ✅ 把 es.exe 放到打包输出目录中
    ],
    hiddenimports=collect_submodules('src') + collect_submodules('pypdf'),  # 自动识别 src 和 pypdf 模块
    hookspath=[],
    runtime_hooks=[],  # 删除运行时钩子
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

# 打包 Python 模块为 .pyz
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# 构建 EXE
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='搜图狗',
    debug=False,
    strip=False,
    upx=True,
    console=False,  # 设置为 False 可关闭控制台窗口（GUI 程序）
)