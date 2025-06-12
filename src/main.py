# -*- coding: utf-8 -*-
from logger import log  # 确保日志配置最先初始化
import tkinter as tk
from gui import build_gui
from controller import WatchDogController
from utils import check_env_permission
from utils import diagnose_everything_cli
import tkinter.messagebox as mb
import sys

if __name__ == '__main__':
    env_info = check_env_permission()
    # 检查 everything_user 是否为 None
    if env_info['everything_user'] is None:
        mb.showwarning("权限警告", "未检测到 Everything 进程，请先启动 Everything（并确保和本程序用户一致）！")
        # 你可以 return 或直接退出
        sys.exit(0)
    elif not env_info['permission_match']:
        mb.showwarning("权限警告", "Everything 用户和本程序用户不一致，可能导致搜索无效！\n请重启 Everything 并用当前用户启动。")
    root = tk.Tk()
    root.title('searchDrawingDog v1.0')
    gui_refs = build_gui(root)
    controller = WatchDogController(gui_refs)
    root.mainloop()
