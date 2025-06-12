# -*- coding: utf-8 -*-
import tkinter as tk  # 导入tkinter库，用于GUI开发
from tkinter import messagebox  # 导入消息框模块
import datetime  # 导入日期时间模块
from main_functions import extract_major_version, compare_versions  # 导入自定义的版本提取和比较函数
from pdf_merge import merge_pdf_files  # 导入PDF合并函数
import os, glob  # 导入操作系统和文件通配符模块
from main_functions import find_latest_iso, find_latest_wm
import math
import re
from utils import normalize_ver   # 导入版本归一化
from logger import log
import subprocess

class WatchDogController:  # 定义主控制器类
    def __init__(self, refs):  # 初始化方法，refs为控件引用字典
        self.refs = refs  # 保存控件引用
        self.page_size = 10  # 每页显示10条
        self.page = 1  # 当前页码
        self.rows = []  # 检索结果列表
        self.total_pages = 1

        refs["search_btn"].config(command=self.on_search)  # 绑定搜索按钮事件
        refs["export_btn"].config(command=self.on_export)  # 绑定导出按钮事件
        refs["prev_btn"].config(command=lambda: self.change_page(-1))  # 绑定上一页按钮事件
        refs["next_btn"].config(command=lambda: self.change_page(1))  # 绑定下一页按钮事件
        refs['tree'].bind('<Double-1>', self.on_open_file)

    def on_search(self):
        # 获取测试包名，默认为 PREDEFINED
        testpkg = self.refs['testpkg_var'].get().strip() or "PREDEFINED"
        pids = list(dict.fromkeys(
        l.strip() for l in self.refs["line_text"].get("1.0", "end").splitlines() if l.strip()
        ))
        iso_dir = self.refs['iso_var'].get().strip()
        wm_dir = self.refs['wm_var'].get().strip()

        # 输入校验，只验证必填项
        if not pids:
            messagebox.showerror("错误", "Pipeline ID 必须不为空。")
            return
        if not iso_dir or not os.path.isdir(iso_dir):
            messagebox.showerror("错误", "请选择有效的 ISO 目录。")
            return
        if not wm_dir or not os.path.isdir(wm_dir):
            messagebox.showerror("错误", "请选择有效的 WM 目录。")
            return

        # 使用 main_functions 中的查找逻辑
        self.rows.clear()
        #log.info("DEBUG: iso_dir = %s", iso_dir)
        #log.info(os.listdir(iso_dir))
        for pid in pids:
            # 查找最新 ISO
            #log.info("正在处理: %s", pid)
            iso_name, iso_rev, is_nover  = find_latest_iso(iso_dir, pid)
            iso_path = os.path.join(iso_dir, iso_name) if iso_name else ''
            

            # 查找最新 WM
            wm_name, wm_rev = find_latest_wm(wm_dir, pid)
            wm_path = os.path.join(wm_dir, wm_name) if wm_name else ''
            #log.info("ISO结果: %s, WM结果: %s", iso_name, wm_name)
            iso_ver_norm = normalize_ver(iso_rev)
            wm_ver_norm = normalize_ver(wm_rev)

            #for debugging
            #log.info('"iso_rev:: %s %s %s', iso_rev, "normalize:", normalize_ver(iso_rev))
            #log.info('"wm_rev:: %s %s %s', wm_rev, "normalize:", normalize_ver(wm_rev))
            #log.info('"compare_versions:: %s', compare_versions(iso_rev, wm_rev))

            if is_nover:
                result = "无修订号"
            elif not iso_path or not wm_path:
                result = "缺失"
            elif iso_ver_norm == "" or wm_ver_norm == "":
                result = "缺失"
            elif iso_ver_norm == wm_ver_norm:
                result = "匹配"
            else:
                result = "不一致"
            self.rows.append((testpkg, pid, iso_path, wm_path, result, iso_rev, wm_rev, is_nover))

        # 重置到第 1 页并刷新显示
        self.page = 1
        self.show_page()
             
    def show_page(self):
        tree = self.refs['tree']
        if not tree:
            return
        # 清空旧数据
        for item in tree.get_children():
            tree.delete(item)

        total = len(self.rows)
        self.total_pages = math.ceil(total / self.page_size) if total else 1
        start = (self.page - 1) * self.page_size
        end = start + self.page_size

        # ========== 新增排序，按优先级：缺失 > 不一致 > 匹配 ==========
        def problem_level(row):
            iso_missing = not row[2]
            wm_missing = not row[3]
            not_match = row[4] != '匹配'
            if iso_missing or wm_missing:
                return 0  # 缺失最前
            elif not_match:
                return 1  # 不一致其次
            else:
                return 2  # 完全匹配最后
        sorted_rows = sorted(self.rows, key=problem_level)
        total = len(sorted_rows)
        self.total_pages = math.ceil(total / self.page_size) if total else 1
        start = (self.page - 1) * self.page_size
        end = start + self.page_size
        page_rows = sorted_rows[start:end]

    
        for row in page_rows:
             # row[7]为is_nover
            if len(row) > 7 and row[7]:
                iso_str = f"{os.path.basename(row[2])}（无修订号，需校核）"
            else:
                iso_str = os.path.basename(row[2]) if row[2] else '缺失'
            wm_str = os.path.basename(row[3]) if row[3] else '缺失'
            if not row[2] or not row[3]:
                tag = 'notfound'
            elif row[4] != '匹配':
                tag = 'not-match'
            elif not row[5] or not row[6]:  # 版本号为空，说明命名不规范或缺失
                tag = 'ver-missing'
            else:
                tag = ''
            tree.insert('', 'end',
                        values=(
                            row[0],      # 试压包
                            row[1],      #管线号（Pipeline ID）
                            iso_str,     # ISO文件名
                            wm_str,      # WM文件名
                            row[4],      # 匹配结果
                            row[2] if row[2] else '',  # ISO绝对路径，隐藏用
                            row[3] if row[3] else '',  # WM绝对路径，隐藏用
                        ),
            # 标记为可点击，以便点击时触发事件
                        tags=(tag,))


        # 更新分页标签和按钮状态
        self.refs['page_label'].config(text=f"第 {self.page} / {self.total_pages} 页")
        self.refs['prev_btn'].config(state=('normal' if self.page > 1 else 'disabled'))
        self.refs['next_btn'].config(state=('normal' if self.page < self.total_pages else 'disabled'))

    def change_page(self, delta):
        # 通用翻页方法，delta 为 -1 上一页，1 下一页
        new_page = self.page + delta
        if 1 <= new_page <= getattr(self, 'total_pages', 1):
            self.page = new_page
            self.show_page()

    def on_prev(self):
        if self.page > 1:
            self.page -= 1
            self.show_page()

    def on_next(self):
        if self.page < self.total_pages:
            self.page += 1
            self.show_page()

    def update_pagination(self):
        self.show_page()

    #TODO:多线程合并PDF文件，另开启线程显示正在合并的提示
    def on_export(self):
        if not self.rows:
            messagebox.showwarning("警告", "没有可合并的文件。请先执行搜索。")
            return

        files = []
        for row in self.rows:
            if row[2]:
                files.append(row[2])
            if row[3]:
                files.append(row[3])

        export_dir = os.path.join(os.getcwd(), "export")
        os.makedirs(export_dir, exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"{self.rows[0][0]}_{timestamp}.pdf"
        save_path = os.path.join(export_dir, default_name)

        bad_files = merge_pdf_files(files, save_path)
        
        try:
            os.startfile(save_path)
        except AttributeError:
            import subprocess, sys
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.run([opener, save_path], creationflags=subprocess.CREATE_NO_WINDOW)

        msg = f"合并后的 PDF 已保存到：\n{save_path}"
        if bad_files:
            msg += "\n\n以下文件无法合并，已跳过：\n" + "\n".join(bad_files)
        messagebox.showinfo("合并结果", msg)

    def on_open_file(self, event):
        tree = self.refs['tree']
        item = tree.identify('item', event.x, event.y)
        col = tree.identify_column(event.x)
        if item and col in ('#3', '#4'):
            values = tree.item(item, 'values')
            if col == '#3':
                path = values[5]  # ISO绝对路径
            else:
                path = values[6]  # WM绝对路径
            if path and os.path.isfile(path):
                try:
                    os.startfile(path)
                except Exception as e:
                    tk.messagebox.showwarning("无法打开", str(e))
            else:
                tk.messagebox.showwarning("无法打开", f"文件不存在：\n{path}")

    #TODO：当查询缺失时，用户可能要手动查询，点击鼠标右键可以复制管线号或文件名等信息
    def on_tree_right_click(self, event):
        pass
