import pytest
from unittest.mock import MagicMock, patch

from controller import WatchDogController
import controller

@pytest.fixture
def make_refs():
    def _make(line_text='', testpkg='TP001', iso_dir='iso', wm_dir='wm'):
        return {
            'testpkg_var': MagicMock(get=MagicMock(return_value=testpkg)),
            'line_text': MagicMock(get=MagicMock(return_value=line_text)),
            'iso_var': MagicMock(get=MagicMock(return_value=iso_dir)),
            'wm_var': MagicMock(get=MagicMock(return_value=wm_dir)),
            'tree': MagicMock(),
            'page_label': MagicMock(),
            'prev_btn': MagicMock(),
            'next_btn': MagicMock(),
            'search_btn': MagicMock(config=MagicMock()),
            'export_btn': MagicMock(config=MagicMock())
        }
    return _make

def test_on_search_valid(make_refs):
    refs = make_refs(
        line_text='PIPE-001\nPIPE-002',
        testpkg='TP001',
        iso_dir='mock/iso',
        wm_dir='mock/wm'
    )
    ctrl = WatchDogController(refs)
    with patch('os.path.isdir', return_value=True), \
         patch('os.listdir', return_value=['some.pdf']), \
         patch('controller.find_latest_iso', return_value=('iso1', '01A')), \
         patch('controller.find_latest_wm', return_value=('wm1', '01A')), \
         patch('controller.compare_versions', return_value=0):
        ctrl.show_page = MagicMock()
        ctrl.on_search()
        assert len(ctrl.rows) == 2
        for row in ctrl.rows:
            assert row[0] == 'TP001'
            assert row[4] == '匹配'
        ctrl.show_page.assert_called_once()

def test_on_search_missing_pipeline_id(make_refs):
    refs = make_refs(line_text='')
    ctrl = WatchDogController(refs)
    with patch('tkinter.messagebox.showerror') as mock_msg:
        ctrl.on_search()
        mock_msg.assert_called_once()
        assert ctrl.rows == []

def test_on_search_invalid_dir(make_refs):
    refs = make_refs(
        line_text='PIPE-001',
        iso_dir='', wm_dir=''
    )
    ctrl = WatchDogController(refs)
    with patch('tkinter.messagebox.showerror') as mock_msg:
        ctrl.on_search()
        mock_msg.assert_called()
        assert ctrl.rows == []

from unittest.mock import MagicMock
from controller import WatchDogController

def make_ctrl_for_show_page(rows=None, page_size=2):
    mock_tree = MagicMock()
    mock_tree.get_children.return_value = ['id1', 'id2']
    mock_page_label = MagicMock()
    mock_prev_btn = MagicMock()
    mock_next_btn = MagicMock()
    mock_search_btn = MagicMock(config=MagicMock())
    mock_export_btn = MagicMock(config=MagicMock())
    refs = {
        'tree': mock_tree,
        'page_label': mock_page_label,
        'prev_btn': mock_prev_btn,
        'next_btn': mock_next_btn,
       'search_btn': mock_search_btn,
       'export_btn': mock_export_btn,
    }
    ctrl = WatchDogController(refs)
    ctrl.page_size = page_size
    ctrl.rows = rows or [
        ('TP001', '01', 'iso1', 'wm1', '匹配', '01', '01'),
        ('TP001', '02', 'iso2', 'wm2', '不一致', '02', '03'),
        ('TP001', '03', 'iso3', 'wm3', '匹配', '03', '03')
    ]
    ctrl.page = 1
    ctrl.total_pages = 2
    return ctrl, mock_tree, mock_page_label, mock_prev_btn, mock_next_btn

def test_show_page_basic():
    ctrl, mock_tree, mock_page_label, mock_prev_btn, mock_next_btn = make_ctrl_for_show_page()

    ctrl.show_page()

    mock_tree.get_children.assert_called()
    mock_tree.delete.assert_any_call('id1')
    mock_tree.delete.assert_any_call('id2')

    # 插入前两条（排序后）
    assert mock_tree.insert.call_count == 2
    args_list = [call.kwargs for call in mock_tree.insert.call_args_list]

    # 排序后，第1条是不一致
    assert args_list[0]['tags'] == ('not-match',)
    # 第2条是匹配
    assert args_list[1]['tags'] == ('',)

    mock_page_label.config.assert_called()
    mock_prev_btn.config.assert_called()
    mock_next_btn.config.assert_called()


def test_show_page_second_page():
    ctrl, mock_tree, *_ = make_ctrl_for_show_page()
    ctrl.page = 2  # 第二页
    ctrl.show_page()
    # 只应插入第3条
    assert mock_tree.insert.call_count == 1
    call_kwargs = mock_tree.insert.call_args[1]
    # 只有第3行
    assert call_kwargs['values'][0] == 'TP001'
    # 标签为匹配
    assert call_kwargs['tags'] == ('',)

def make_ctrl_for_change_page():
    refs = {
        'search_btn': MagicMock(config=MagicMock()),
        'export_btn': MagicMock(config=MagicMock()),
        'tree': MagicMock(),
        'page_label': MagicMock(),
        'prev_btn': MagicMock(),
        'next_btn': MagicMock()
    }
    ctrl = WatchDogController(refs)
    ctrl.page_size = 2
    ctrl.total_pages = 3
    ctrl.rows = [1, 2, 3, 4, 5]
    ctrl.show_page = MagicMock()
    return ctrl

def test_change_page_forward_and_backward():
    ctrl = make_ctrl_for_change_page()
    ctrl.page = 1
    ctrl.change_page(1)   # 前进一页
    assert ctrl.page == 2
    ctrl.show_page.assert_called()
    ctrl.show_page.reset_mock()
    ctrl.change_page(-1)  # 回退一页
    assert ctrl.page == 1
    ctrl.show_page.assert_called()

def test_change_page_overflow():
    ctrl = make_ctrl_for_change_page()
    ctrl.page = 3
    ctrl.change_page(1)  # 超过最大页
    assert ctrl.page == 3  # 应该保持不变
    ctrl.show_page.assert_not_called()
    ctrl.show_page.reset_mock()
    ctrl.page = 1
    ctrl.change_page(-1)  # 小于1
    assert ctrl.page == 1  # 仍然保持不变
    ctrl.show_page.assert_not_called()


def make_ctrl_for_nav():
    refs = {
        'search_btn': MagicMock(config=MagicMock()),
        'export_btn': MagicMock(config=MagicMock()),
        'tree': MagicMock(),
        'page_label': MagicMock(),
        'prev_btn': MagicMock(),
        'next_btn': MagicMock()
    }
    ctrl = WatchDogController(refs)
    ctrl.page = 2
    ctrl.total_pages = 3
    ctrl.show_page = MagicMock()
    return ctrl

def test_on_prev_page_decrement():
    ctrl = make_ctrl_for_nav()
    ctrl.on_prev()
    assert ctrl.page == 1
    ctrl.show_page.assert_called_once()

def test_on_prev_no_decrement_at_first_page():
    ctrl = make_ctrl_for_nav()
    ctrl.page = 1
    ctrl.show_page.reset_mock()
    ctrl.on_prev()
    assert ctrl.page == 1  # 不应该变
    ctrl.show_page.assert_not_called()

def test_on_next_page_increment():
    ctrl = make_ctrl_for_nav()
    ctrl.page = 2
    ctrl.total_pages = 3
    ctrl.show_page.reset_mock()
    ctrl.on_next()
    assert ctrl.page == 3
    ctrl.show_page.assert_called_once()

def test_on_next_no_increment_at_last_page():
    ctrl = make_ctrl_for_nav()
    ctrl.page = 3
    ctrl.total_pages = 3
    ctrl.show_page.reset_mock()
    ctrl.on_next()
    assert ctrl.page == 3  # 不应该变
    ctrl.show_page.assert_not_called()

def test_update_pagination_calls_show_page():
    ctrl = make_ctrl_for_nav()
    ctrl.show_page = MagicMock()
    ctrl.update_pagination()
    ctrl.show_page.assert_called_once()


def make_ctrl_for_export(rows=None):
    refs = {
        'search_btn': MagicMock(config=MagicMock()),
        'export_btn': MagicMock(config=MagicMock()),
        'tree': MagicMock(),
        'page_label': MagicMock(),
        'prev_btn': MagicMock(),
        'next_btn': MagicMock()
    }
    ctrl = WatchDogController(refs)
    ctrl.rows = rows or []
    return ctrl

def test_on_export_no_rows():
    ctrl = make_ctrl_for_export(rows=[])
    with patch('tkinter.messagebox.showwarning') as mock_warn:
        ctrl.on_export()
        mock_warn.assert_called_once_with("警告", "没有可合并的文件。请先执行搜索。")

def test_on_export_success():
    # 构造一个正常的 rows（至少有一个文件名）
    ctrl = make_ctrl_for_export(rows=[
        ('PKG1', 'pid1', 'file1.pdf', 'file2.pdf', '匹配', 'v1', 'v2')
    ])
    # patch merge_pdf_files，os.startfile，messagebox.showinfo
    with patch('controller.merge_pdf_files', return_value=[]), \
         patch('os.startfile') as mock_start, \
         patch('tkinter.messagebox.showinfo') as mock_info:
        ctrl.on_export()
        # 检查os.startfile被调用
        mock_start.assert_called_once()
        # 检查弹窗
        called_args = mock_info.call_args[0]
        assert "合并后的 PDF 已保存到" in called_args[1]

def test_on_export_with_bad_files():
    ctrl = make_ctrl_for_export(rows=[
        ('PKG1', 'pid1', 'file1.pdf', 'file2.pdf', '匹配', 'v1', 'v2')
    ])
    with patch('controller.merge_pdf_files', return_value=['file1.pdf']), \
         patch('os.startfile'), \
         patch('tkinter.messagebox.showinfo') as mock_info:
        ctrl.on_export()
        # 检查弹窗内容包含坏文件名
        args = mock_info.call_args[0][1]
        assert "file1.pdf" in args
        assert "已跳过" in args
        
def test_on_export_fallback_open():
    ctrl = make_ctrl_for_export(rows=[
        ('PKG1', 'pid1', 'file1.pdf', 'file2.pdf', '匹配', 'v1', 'v2')
    ])
    with patch('controller.merge_pdf_files', return_value=[]), \
         patch('os.startfile', side_effect=AttributeError), \
         patch('tkinter.messagebox.showinfo'), \
         patch('subprocess.run') as mock_run:
        ctrl.on_export()
        mock_run.assert_called()
