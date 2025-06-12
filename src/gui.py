# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, filedialog

def build_gui(root):
    # Test Package
    frame1 = ttk.Frame(root)
    frame1.pack(fill="x", padx=10, pady=(10, 2))
    ttk.Label(frame1, text="试压包").pack(side="left")
    testpkg_var = tk.StringVar()
    testpkg_entry = ttk.Entry(frame1, textvariable=testpkg_var, width=18)
    testpkg_entry.pack(side="left", padx=3)

    # Pipeline ID
    frame2 = ttk.Frame(root)
    frame2.pack(fill="x", padx=10, pady=(2, 2))
    ttk.Label(frame2, text="管线").pack(side="left")
    line_text = tk.Text(frame2, height=5, width=40, undo=True)
    line_text.pack(side="left", padx=3)

    # ISO目录
    frame3 = ttk.Frame(root)
    frame3.pack(fill="x", padx=10, pady=(2, 2))
    ttk.Label(frame3, text="ISO目录:").pack(side="left")
    iso_var = tk.StringVar()
    iso_entry = ttk.Entry(frame3, textvariable=iso_var, width=40)
    iso_entry.pack(side="left", padx=2)
    ttk.Button(frame3, text="浏览", command=lambda: choose_dir(iso_var)).pack(side="left", padx=2)

    # WM目录
    frame4 = ttk.Frame(root)
    frame4.pack(fill="x", padx=10, pady=(2, 2))
    ttk.Label(frame4, text="WeldingMap目录:").pack(side="left")
    wm_var = tk.StringVar()
    wm_entry = ttk.Entry(frame4, textvariable=wm_var, width=40)
    wm_entry.pack(side="left", padx=2)
    ttk.Button(frame4, text="浏览", command=lambda: choose_dir(wm_var)).pack(side="left", padx=2)

    # 搜索+导出
    frame5 = ttk.Frame(root)
    frame5.pack(fill="x", padx=10, pady=(2, 2))
    search_btn = ttk.Button(frame5, text="搜索")
    search_btn.pack(side="left", padx=5)
    export_btn = ttk.Button(frame5, text="合并导出")
    export_btn.pack(side="left", padx=5)

    # 结果表格
    columns = ("试压包", "管线号","ISO", "WeldingMap", "结果", "ISO_path", "WM_path")
    tree = ttk.Treeview(root, columns=columns, show="headings")
    tree.tag_configure('notfound', background='#ffe6e6', foreground='#c00')    # 缺失：红色高亮
    tree.tag_configure('not-match', background='#fffbe6', foreground='#c60')   # 不一致：橙色高亮
    tree.tag_configure('ver-missing', background='#e6f0ff', foreground='#003399')  # 示例：淡蓝+深蓝字
    style = ttk.Style()
    style.configure('Treeview', rowheight=30)
    style.map('Treeview',
        background=[('selected', '#284862')],
        foreground=[('selected', '#fff')])
    for col in columns[:5]:
        tree.heading(col, text=col)
    tree.column("试压包", width=90, anchor="w")
    tree.column("管线号", width=200, anchor="w")
    tree.column("ISO", width=340, anchor="w")
    tree.column("WeldingMap", width=340, anchor="w")
    tree.column("结果", width=90, anchor="center")
    tree.pack(fill="both", expand=True, padx=10, pady=4)
    tree["displaycolumns"] = columns[:5]  # 只显示前5列，后2列隐藏

    # 分页
    page_frame = ttk.Frame(root)
    page_frame.pack(fill="x", padx=10, pady=(2, 8))
    page_label = ttk.Label(page_frame, text="第 1 / 1 页")
    page_label.pack(side="left", padx=3)
    prev_btn = ttk.Button(page_frame, text="上一页")
    prev_btn.pack(side="left", padx=3)
    next_btn = ttk.Button(page_frame, text="下一页")
    next_btn.pack(side="left", padx=3)  

    def choose_dir(var):
        d = filedialog.askdirectory()
        if d:
            var.set(d)

    return {
        "testpkg_var": testpkg_var,
        "line_text": line_text,
        "iso_var": iso_var,
        "wm_var": wm_var,
        "search_btn": search_btn,
        "export_btn": export_btn,
        "tree": tree,
        "page_label": page_label,
        "prev_btn": prev_btn,
        "next_btn": next_btn
    }

