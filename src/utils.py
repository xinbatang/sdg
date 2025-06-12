# utils.py
import ctypes
import psutil
import getpass
import os
import shutil
import subprocess
import re
from logger import log

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def get_everything_username():
    for p in psutil.process_iter(['name', 'username']):
        if p.info['name'] and 'everything' in p.info['name'].lower():
            return p.info['username']
    return None

def check_env_permission():
    me_admin = is_admin()
    current_user = getpass.getuser()
    everything_user = get_everything_username()
    log.info("当前程序是否管理员: %s", me_admin)
    log.info("当前程序用户: %s", current_user)
    log.info("Everything进程用户: %s", everything_user)
    # 宽松比较：只比较用户名部分
    if everything_user and not everything_user.endswith(current_user):
        log.error("警告：Everything进程用户与本程序用户不一致，可能导致 CLI 搜索失败。")
    else:
        log.info("Everything进程用户与本程序用户一致，权限OK。")
    return {
        "is_admin": me_admin,
        "current_user": current_user,
        "everything_user": everything_user,
        "permission_match": everything_user.endswith(current_user) if everything_user else None
    }

def diagnose_everything_cli(ES_CLI, directory, pattern):
    """
    打印 Everything CLI 调用的详细诊断信息
    """
    #log.info("\n==== Everything 权限&环境诊断 ====")
    #log.info('"当前目录:: %s', os.getcwd())
    #log.info('"ES_CLI 路径:: %s', shutil.which(ES_CLI))
    #log.info('"directory 参数:: %s', repr(directory))
    #log.info('"pattern 参数:: %s', repr(pattern))
    cmd = [
        ES_CLI,
        '-path', directory,
        f"{pattern}*.pdf",
        '-sort', 'date-modified-descending'
    ]
    #log.info('"实际调用命令:: %s', ' '.join(cmd))
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=10, creationflags=subprocess.CREATE_NO_WINDOW)
        #log.info('"STDOUT:: %s', res.stdout)
        #log.info('"STDERR:: %s', res.stderr)
        #log.info('"返回码:: %s', res.returncode)
    except Exception as e:
        log.error('"子进程调用异常:: %s', e)
    #log.info("================================\n")


def normalize_single_ver(ver: str) -> str:
    if not ver:
        return ""
    ver = ver.upper()
    if ver.isdigit():
        return str(int(ver))  # '00' -> '0', '01' -> '1'
    # 数字+字母，如 00A → A, 01B → 1B
    m = re.match(r'^0*(\d*[A-Z]+)$', ver)
    if m:
        return m.group(1)
    # 全字母，如 0B → B
    m = re.match(r'^0*([A-Z]+)$', ver)
    if m:
        return m.group(1)
    # 全数字，如 001 → 1
    m = re.match(r'^0*(\d+)$', ver)
    if m:
        return m.group(1)
    return ver.lstrip("0")

def normalize_ver(ver: str) -> str:
    """
    提取主版本号（忽略下划线后的子版本），用于 ISO 比较。
    '01B_01S' → '1B'，'00A_00' → 'A'
    """
    if not ver:
        return ""
    main = ver.upper().split('_')[0]
    return normalize_single_ver(main)
