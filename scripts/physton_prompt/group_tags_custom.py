"""【标签快捷列表】自定义分组的读写。

只操作 `group_tags/append.yaml`：用户自定义的分组追加在内置列表末尾，
不覆盖内置的 default.yaml / 语言包，插件更新时也不会冲突。
"""
import os
import threading

current_dir = os.path.dirname(os.path.abspath(__file__))
custom_file = os.path.join(current_dir, '../../group_tags/', 'append.yaml')

# 防止一次写入过大内容（正常几十 KB 足够）
MAX_BYTES = 2 * 1024 * 1024

_lock = threading.RLock()


def read_custom():
    """返回 append.yaml 的原始文本；文件不存在时返回空串。"""
    if not os.path.exists(custom_file):
        return ''
    try:
        with open(custom_file, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return ''


def save_custom(content):
    """原子写入 append.yaml；内容为空时删除该文件（回到只用内置列表）。"""
    content = str(content or '')
    if len(content.encode('utf-8')) > MAX_BYTES:
        raise ValueError('content too large')
    with _lock:
        if not content.strip():
            if os.path.exists(custom_file):
                os.remove(custom_file)
            return ''
        tmp = custom_file + '.tmp'
        with open(tmp, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)
        os.replace(tmp, custom_file)
    return content
