"""本地 AI 大模型翻译（与 sd_forge_lora_new 共用同一个 llama.cpp 实例）。

冲突处理：
- 模型实例、推理锁、空闲卸载线程都在 `lna_llm_service.core` 里，只有一份；
  两个插件 import 的是同一个 Python 模块对象，天然不会出现「两份模型 / 两个卸载计时」。
- 推理走 core 内部的全局 RLock：本插件与 lora_new 的翻译请求**串行排队**，
  不会同时动同一个 llama_cpp 实例。
- 归属：lora_new 启用时由它写入 owner='lora_new'，空闲卸载/手动卸载以它的设置为准；
  本插件此时只读状态并禁用相关按钮（仅存在于 UI 层）。
"""
import sys
import threading
from pathlib import Path

_SERVICE = None
_IMPORT_ERROR = ''
_IMPORT_LOCK = threading.Lock()

SIBLING_EXTENSION = 'sd_forge_lora_new'


def _extensions_dir():
    # <extensions>/sd-webui-prompt-all-in-one-forge/scripts/physton_prompt/local_llm.py
    return Path(__file__).resolve().parents[3]


def sibling_extension_dir():
    return _extensions_dir() / SIBLING_EXTENSION


def _import_service():
    global _SERVICE, _IMPORT_ERROR
    if _SERVICE is not None:
        return _SERVICE
    with _IMPORT_LOCK:
        if _SERVICE is not None:
            return _SERVICE
        ext = sibling_extension_dir()
        if not ext.is_dir():
            _IMPORT_ERROR = 'sd_forge_lora_new is not installed'
            return None
        path = str(ext)
        if path not in sys.path:
            # 该扩展未被启用时不会经由 script_loading 进入 sys.path，这里手动补上
            sys.path.insert(0, path)
        try:
            from lna_llm_service import core
        except Exception as e:
            _IMPORT_ERROR = f'{e}'
            return None
        _SERVICE = core
        _IMPORT_ERROR = ''
        return _SERVICE


def get_service():
    return _import_service()


def import_error():
    return _IMPORT_ERROR


def lora_new_enabled():
    """sd_forge_lora_new 是否存在且已启用（决定空闲卸载计时归属哪一方）。"""
    try:
        from modules import extensions as webui_extensions
        listed = webui_extensions.list_extensions()
    except Exception:
        listed = None
    if not listed:
        return sibling_extension_dir().is_dir()
    for ext in listed:
        path = str(getattr(ext, 'path', '') or '').replace('\\', '/')
        if path.rstrip('/').endswith('/' + SIBLING_EXTENSION):
            return bool(getattr(ext, 'enabled', True))
        # 目录名可能被改过（例如带分支后缀），按路径判定优先于按名字判定
    for ext in listed:
        name = str(getattr(ext, 'name', '') or '')
        if name == SIBLING_EXTENSION:
            return bool(getattr(ext, 'enabled', True))
    return False


def owner():
    """空闲卸载计时的归属方：'lora_new' 或 'prompt'。"""
    return 'lora_new' if lora_new_enabled() else 'prompt'


def frozen():
    """本插件是否冻结「空闲时自动卸载 / 手动卸载」（归属 lora_new 时冻结）。"""
    return owner() == 'lora_new'


def status():
    service = get_service()
    if service is None:
        return {
            'ok': False,
            'error': _IMPORT_ERROR or 'Local LLM service is not available',
            'enabled': False,
            'installed': sibling_extension_dir().is_dir(),
        }
    service.ensure_watchdog()
    st = service.status()
    st['ok'] = True
    st['enabled'] = True
    st['frozen'] = frozen()
    st['owner'] = owner()
    return st


def run_inference(user_prompt, system_prompt, json_mode=False):
    """持共享锁做一次推理；返回 {'ok': bool, 'text': str, 'error': str}。"""
    service = get_service()
    if service is None:
        return {'ok': False, 'text': '', 'error': _IMPORT_ERROR or 'Local LLM service is not available'}
    return service.run_inference(user_prompt, system_prompt, json_mode=json_mode)
