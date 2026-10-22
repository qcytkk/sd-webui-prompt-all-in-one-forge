"""【机翻词典】——缓存【连网翻译】与【本地AI大模型翻译】的翻译对照。

存储：`storage/machine_dict.csv`（UTF-8 BOM，Excel 可直接打开）
列：from_lang,to_lang,source,target

翻译流程里命中本词典就直接复用，不再消耗网络 / 显存资源；
未命中时才交给后面的连网翻译 / 本地大模型翻译，成功后再写回本文件。
"""
import csv
import os
import subprocess
import sys
import threading

_base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../', '../'))
_dict_dir = os.path.join(_base_dir, 'storage')
_dict_path = os.path.join(_dict_dir, 'machine_dict.csv')

HEADER = ['from_lang', 'to_lang', 'source', 'target']

_lock = threading.RLock()
_cache = None
_cache_sig = None


def _norm(text):
    return str(text or '').strip()


def _key(from_lang, to_lang, source):
    return (str(from_lang or ''), str(to_lang or ''), _norm(source).lower())


def _signature():
    try:
        st = os.stat(_dict_path)
        return st.st_mtime, st.st_size
    except OSError:
        return None


def _load():
    """读取词典（按文件 mtime/size 缓存，手工改文件后自动失效）。"""
    global _cache, _cache_sig
    sig = _signature()
    if _cache is not None and sig == _cache_sig:
        return _cache

    data = {}
    if os.path.exists(_dict_path):
        try:
            with open(_dict_path, 'r', encoding='utf-8-sig', newline='') as f:
                for row in csv.reader(f):
                    if len(row) < 4:
                        continue
                    if _norm(row[0]) == HEADER[0] and _norm(row[2]) == HEADER[2]:
                        continue
                    source = _norm(row[2])
                    target = _norm(row[3])
                    if not source or not target:
                        continue
                    data[_key(row[0], row[1], source)] = target
        except Exception:
            pass

    _cache = data
    _cache_sig = sig
    return data


def _invalidate():
    global _cache, _cache_sig
    _cache = None
    _cache_sig = None


def _write(data):
    """整表原子写回（临时文件 + replace），避免写到一半损坏文件。"""
    if not os.path.exists(_dict_dir):
        os.makedirs(_dict_dir)
    tmp = _dict_path + '.tmp'
    with open(tmp, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(HEADER)
        for (from_lang, to_lang, source), target in data.items():
            writer.writerow([from_lang, to_lang, source, target])
    os.replace(tmp, _dict_path)


def lookup(texts, from_lang, to_lang):
    """批量查询，未命中的位置返回空字符串。"""
    data = _load()
    results = []
    for text in texts or []:
        results.append(data.get(_key(from_lang, to_lang, text), ''))
    return results


def add_many(from_lang, to_lang, items):
    """写入一批翻译对照，返回新增条数（已存在的不重复写）。"""
    if not items:
        return 0
    added = 0
    with _lock:
        data = dict(_load())
        for item in items:
            if not isinstance(item, dict):
                continue
            source = _norm(item.get('source'))
            target = _norm(item.get('target'))
            if not source or not target or source == target:
                continue
            key = _key(from_lang, to_lang, source)
            if key in data:
                continue
            data[key] = target
            added += 1
        if added:
            _write(data)
            _invalidate()
    return added


def stats():
    data = _load()
    size = 0
    if os.path.exists(_dict_path):
        try:
            size = os.path.getsize(_dict_path)
        except OSError:
            size = 0
    return {
        'count': len(data),
        'size': size,
        'file': os.path.basename(_dict_path),
    }


def storage_dir():
    return _dict_dir


def entries():
    """返回全部词条（按文件顺序），供【编辑词典】列表展示。"""
    return [
        {'from_lang': from_lang, 'to_lang': to_lang, 'source': source, 'target': target}
        for (from_lang, to_lang, source), target in _load().items()
    ]


def update(from_lang, to_lang, source, target):
    """修改单条译文；词条不存在或译文为空时返回 False。"""
    target = _norm(target)
    if not target:
        return False
    with _lock:
        data = dict(_load())
        key = _key(from_lang, to_lang, source)
        if key not in data:
            return False
        if data[key] != target:
            data[key] = target
            _write(data)
            _invalidate()
    return True


def delete(from_lang, to_lang, source):
    """删除单条词条；词条不存在时返回 False。"""
    with _lock:
        data = dict(_load())
        key = _key(from_lang, to_lang, source)
        if key not in data:
            return False
        del data[key]
        _write(data)
        _invalidate()
    return True


def open_folder():
    """在系统文件管理器里打开词典所在目录；成功返回空串，失败返回错误信息。"""
    try:
        os.makedirs(_dict_dir, exist_ok=True)
        if os.name == 'nt':
            os.startfile(_dict_dir)
        else:
            opener = 'open' if sys.platform == 'darwin' else 'xdg-open'
            subprocess.Popen([opener, _dict_dir])
    except Exception as e:
        return str(e)
    return ''
