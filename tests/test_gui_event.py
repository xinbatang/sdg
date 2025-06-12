import pytest
from unittest.mock import MagicMock, patch

def make_fake_event(x, y):
    class Event:
        pass
    e = Event()
    e.x = x
    e.y = y
    return e

def test_on_open_file_windows():
    tree = MagicMock()
    # 模拟点击第2列，有文件名
    tree.identify.return_value = 'item1'
    tree.identify_column.return_value = '#2'
    tree.item.return_value = {'values': ['PKG1', 'test.pdf', 'wm.pdf', '匹配']}
    event = make_fake_event(10, 10)

    with patch('os.name', 'nt'), \
         patch('os.startfile') as mock_startfile:
        # 注意：on_open_file是build_gui的内部函数，假设我们能单独导入/定义
        def on_open_file(event):
            item = tree.identify('item', event.x, event.y)
            col = tree.identify_column(event.x)
            if item and col in ('#2', '#3'):
                filename = tree.item(item)['values'][int(col[-1]) - 1]
                if filename:
                    import os, subprocess
                    try:
                        if os.name == 'nt':
                            os.startfile(filename)
                        else:
                            subprocess.call(['xdg-open', filename])
                    except Exception as e:
                        import tkinter as tk
                        tk.messagebox.showwarning("无法打开", str(e))
        on_open_file(event)
        # 应该调用 os.startfile
        mock_startfile.assert_called_once_with('test.pdf')

def test_on_open_file_linux():
    tree = MagicMock()
    tree.identify.return_value = 'item1'
    tree.identify_column.return_value = '#3'
    tree.item.return_value = {'values': ['PKG1', 'test.pdf', 'wm.pdf', '匹配']}
    event = make_fake_event(10, 10)

    with patch('os.name', 'posix'), \
         patch('subprocess.call') as mock_call:
        def on_open_file(event):
            item = tree.identify('item', event.x, event.y)
            col = tree.identify_column(event.x)
            if item and col in ('#2', '#3'):
                filename = tree.item(item)['values'][int(col[-1]) - 1]
                if filename:
                    import os, subprocess
                    try:
                        if os.name == 'nt':
                            os.startfile(filename)
                        else:
                            subprocess.call(['xdg-open', filename])
                    except Exception as e:
                        import tkinter as tk
                        tk.messagebox.showwarning("无法打开", str(e))
        on_open_file(event)
        mock_call.assert_called_once_with(['xdg-open', 'wm.pdf'])

def test_on_open_file_exception():
    tree = MagicMock()
    tree.identify.return_value = 'item1'
    tree.identify_column.return_value = '#2'
    tree.item.return_value = {'values': ['PKG1', 'test.pdf', 'wm.pdf', '匹配']}
    event = make_fake_event(10, 10)

    with patch('os.name', 'nt'), \
         patch('os.startfile', side_effect=OSError("No such file")), \
         patch('tkinter.messagebox.showwarning') as mock_warn:
        def on_open_file(event):
            item = tree.identify('item', event.x, event.y)
            col = tree.identify_column(event.x)
            if item and col in ('#2', '#3'):
                filename = tree.item(item)['values'][int(col[-1]) - 1]
                if filename:
                    import os, subprocess
                    try:
                        if os.name == 'nt':
                            os.startfile(filename)
                        else:
                            subprocess.call(['xdg-open', filename])
                    except Exception as e:
                        import tkinter as tk
                        tk.messagebox.showwarning("无法打开", str(e))
        on_open_file(event)
        mock_warn.assert_called_once()
        assert "无法打开" in mock_warn.call_args[0][0]
        assert "No such file" in mock_warn.call_args[0][1]
