# -*- coding: utf-8 -*-
import re
import subprocess
from pathlib import Path
import traceback
from datetime import datetime
import os
import shutil
from utils import diagnose_everything_cli
from utils import normalize_ver, normalize_single_ver
import sys
from logger import log

if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "third_party"))

ES_CLI = os.path.join(BASE_DIR, "es.exe")

def log_error(msg):
    """
    功能：将错误信息写入日志文件（watchDrawingDog.log），带时间戳。
    """
    try:
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 获取当前时间戳
        with open("watchDrawingDog.log", "a", encoding="utf-8") as f:  # 以追加模式打开日志文件
            f.write(f"[{ts}] {msg}\n")  # 写入日志内容
    except:
        pass  # 如果写日志失败则忽略

def extract_major_version(filename: str, mode: str) -> str:
    """
    功能：根据 mode='iso' 或 'wm' 提取主版本号
      - ISO:
        1. 6段结构，最后一段为主版本号
        2. 5段结构，返回 '00'
        3. 下划线修订号（如 _01A），返回 '01A'
      - WM:
        1. Rev 修订号（如 Rev01A），返回 '01A'
        2. 下划线修订号（如 _01A），返回 '01A'
        3. 其它结构返回空字符串
    """
    try:
        name = Path(filename).stem
        parts = name.split('-')
        if mode == 'iso':
            # 1. 优先提取下划线修订号
            m = re.search(r'_(\d+[A-Za-z]*)', name)           
            if m:
                return m.group(1)
            # 2. 6段结构
            if len(parts) == 6 and all(parts):
                return parts[-1]
            # 3. 5段结构
            if len(parts) == 5 and all(parts):
                return None
            return None
        else:
            # 未知模式直接返回空
            return ""
    except Exception:
        log_error(traceback.format_exc())
        return None

#用于将来的版本号比较，实现搜索结果排序
def compare_versions(a: str, b: str) -> int:
    """
    TODO： "01AA" vs "01AB"， S.p.A.公司的版本号复杂，BFA vs FAC，需要重新设计比较规则。
    功能：比较两个版本号字符串的大小。
    参数：
        a, b: 版本号字符串（如 '1A', '2B'）
   返回值：
        -1: a < b
        0: a == b
        1: a > b
    """
    """
    比较两个主版本（ISO 使用），先比数字，再比字母。
    """
    if a is None and b is None:
        return 0
    if a is None:
        return -1
    if b is None:
        return 1
        
    try:
        a_n = normalize_ver(a)
        b_n = normalize_ver(b)
        
        na = int(re.match(r'\d+', a_n).group()) if re.match(r'\d+', a_n) else 0
        nb = int(re.match(r'\d+', b_n).group()) if re.match(r'\d+', b_n) else 0
        if na != nb:
            return 1 if na > nb else -1
        # 数字部分相同，比较字母部分
        sa = re.sub(r'^\d+', '', a_n)
        sb = re.sub(r'^\d+', '', b_n)
        if sa == sb:
            return 0
        if not sa:
            return -1
        if not sb:
            return 1
        return 1 if sa > sb else -1
    except Exception:
        log_error(traceback.format_exc())  # 出错写日志
        return 0

def check_everything_cli():
    if not shutil.which(ES_CLI):
        return False, f"未找到 Everything CLI（{ES_CLI}），请将 es.exe 放到程序目录或添加到 PATH。"
    try:
        res = subprocess.run([ES_CLI, "-version"], capture_output=True, text=True, timeout=5, creationflags=subprocess.CREATE_NO_WINDOW)
        if res.returncode == 0 and res.stdout:
            return True, None
        else:
            return False, "Everything CLI 运行异常，请检查 es.exe 是否为最新版本。"
    except Exception as e:
        return False, f"Everything CLI 调用异常：{e}"

def extract_wm_versions(filename):
    """
    提取 WM 文件的主版本号（如 00B）和子版本号（如 01S）
    """
    name = Path(filename).stem
    m1 = re.search(r'Rev(\d+[A-Za-z]*)', name, re.IGNORECASE)
    main_ver = m1.group(1) if m1 else ""
    m2 = re.search(r'_(\d+[A-Za-z]*)$', name)
    sub_ver = m2.group(1) if m2 else ""
    return main_ver, sub_ver

def diagnose_everything_cli(ES_CLI, directory, pattern):
    """
    打印 Everything CLI 调用的详细诊断信息
    """
    cmd = [
        ES_CLI,
        '-path', directory,
        f"{pattern}*.pdf",
        '-sort', 'date-modified-descending'
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=10, creationflags=subprocess.CREATE_NO_WINDOW)
    except Exception as e:
        log.error('"子进程调用异常:: %s', e)

def everything_search(directory: str, pattern: str):
    """
    功能：调用 Everything CLI 工具在指定目录下查找匹配 pattern 的 PDF 文件。
    参数：
        directory: 目录路径
        pattern: 文件名前缀
    返回：
        匹配到的文件路径列表
    """
    ok, err = check_everything_cli()
    if not ok:
        # 这里可以用日志、弹窗、返回空列表等
        try:
            import tkinter.messagebox as mb
            mb.showerror("依赖检查失败", err)
        except Exception:
            log.error("[Everything错误]%s", err)
        return []

    diagnose_everything_cli(ES_CLI, directory, pattern)

    try:
        cmd = [
            ES_CLI,
            '-path', directory,
            f"{pattern}*.pdf",
            '-sort', 'date-modified-descending'
        ]

        res = subprocess.run(cmd, capture_output=True, text=True, timeout=10, creationflags=subprocess.CREATE_NO_WINDOW)  # 执行命令
        output = res.stdout.strip()
        # 判断是否为 help 文本
        if ("Usage:" in output) or ("Everything" in output and ".pdf" not in output):
            log.info("警告：es.exe 返回了帮助信息，命令行参数有误或 Everything 未运行。")
            return []
        return list(set([l.strip() for l in res.stdout.splitlines() if l.strip()]))  # 返回所有非空行
    except Exception:
        log_error(traceback.format_exc())  # 出错写日志
        return []

def find_latest_iso(iso_dir: str, line_id: str):
    """
    功能：在 ISO 目录下查找指定管线号的最新版本 PDF 文件。
    返回：文件名（去扩展名）和原始版本号（未归一化，用于展示）
    """
    best_file, best_rev, best_norm = "", "", ""
    no_ver_file = ""
    for fp in everything_search(iso_dir, line_id):  # 遍历所有匹配文件
        fn = Path(fp).name
        rev = extract_major_version(fn, 'iso')  # 原始版本号
        print(f"fn={fn!r}, rev={rev!r}") 
        norm = normalize_ver(rev) if rev else None               # 归一化版本号

        if norm:  # 有修订号
            if not best_norm or compare_versions(norm, best_norm) > 0:
                best_file, best_rev, best_norm = fn, rev, norm
        else:     # 无修订号
            no_ver_file = fn
        #log.info("line_id=%s: fname=%s rev=%s", line_id, fn, rev)
    if best_file:     # 有修订号
        return best_file, best_rev, False
    elif no_ver_file: # 兜底无修订号
        return no_ver_file, None, True
    else:
       return "", "", False


def compare_wm_versions(a: str, b: str) -> int:
    """
    比较 WM 文件的完整版本（如 00A_00S），先比主版本，再比子版本。
    """
    if not a and not b:
        return 0
    if not a:
        return -1
    if not b:
        return 1

    a = a.upper()
    b = b.upper()
    a_main, a_sub = (a.split('_') + [''])[:2]
    b_main, b_sub = (b.split('_') + [''])[:2]

    # 主版本比较
    a_main_n = normalize_single_ver(a_main)
    b_main_n = normalize_single_ver(b_main)
    cmp_main = compare_versions(a_main_n, b_main_n)
    if cmp_main != 0:
        return cmp_main

    # 子版本比较（若主版本相等）
    a_sub_n = normalize_single_ver(a_sub)
    b_sub_n = normalize_single_ver(b_sub)
    return compare_versions(a_sub_n, b_sub_n)

def find_latest_wm(wm_dir: str, line_id: str):
    """
    功能：在 WM 目录下查找指定管线号的最新版本 PDF 文件。
    返回：文件名（去扩展名）和原始版本号（用于展示）
    """
    best_file, best_rev = "", ""

    for fp in everything_search(wm_dir, line_id):  # 遍历匹配文件
        fn = Path(fp).name
        main_rev, sub_rev = extract_wm_versions(fn)  # 提取 Rev00A_00 或 _01B_01S
        combined_rev = f"{main_rev}_{sub_rev}" if sub_rev else main_rev
        if combined_rev and (not best_rev or compare_wm_versions(combined_rev, best_rev) > 0):
            best_file, best_rev = fn, combined_rev
        #log.info("line_id=%s: fname=%s wm_ver=%s", line_id, fn, combined_rev)

    return best_file, best_rev
