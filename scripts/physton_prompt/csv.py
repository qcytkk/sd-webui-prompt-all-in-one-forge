import os
from pathlib import Path

base_dir = str(Path().absolute())
self_base_dir = os.path.abspath(os.path.join(os.path.join(os.path.dirname(__file__)), '../', '../'))
self_tags_dir = os.path.join(self_base_dir, 'tags')

# ---------- 词典优先级 ----------
# 优先使用本插件 tags/ 下的 sd-webui-prompt-all-in-one-forge_en_zh_dictionary.csv（随插件分发，条目更多、译文更干净）；
# 只有它不存在时，才回退到 TagComplete 的 danbooru.zh_CN_SFW.csv。
PREFERRED_DICT = 'sd-webui-prompt-all-in-one-forge_en_zh_dictionary.csv'
FALLBACK_DICT = 'danbooru.zh_CN_SFW.csv'

tagcomplete_tags_dir = os.path.join(base_dir, 'extensions', 'a1111-sd-webui-tagcomplete', 'tags')
# sd_forge_lora_new 插件的数据目录：只取其中的 .csv 词典（同目录还有 json 等其它文件）
lora_new_data_dir = os.path.join(base_dir, 'extensions', 'sd_forge_lora_new', 'data')

dirs = [
    self_tags_dir,
    tagcomplete_tags_dir,
    lora_new_data_dir,
]


def _basename(key):
    """取 key 的文件名（兼容 \\ 与 / 两种分隔符）。"""
    return os.path.basename(str(key or '').replace('\\', '/'))


def preferred_dict_path():
    """优先词典的绝对路径；不存在返回 None。"""
    path = os.path.join(self_tags_dir, PREFERRED_DICT)
    return path if os.path.exists(path) else None


def fallback_dict_path():
    """回退词典的绝对路径；不存在返回 None。"""
    path = os.path.join(tagcomplete_tags_dir, FALLBACK_DICT)
    return path if os.path.exists(path) else None


def get_csvs():
    csvs = []
    preferred = preferred_dict_path()
    for dir in dirs:
        if not os.path.exists(dir):
            continue
        for file in os.listdir(dir):
            if not file.lower().endswith('.csv'):
                continue
            # 优先词典存在时，不再列出已被它取代的回退词典
            if preferred and file == FALLBACK_DICT:
                continue
            path = os.path.join(dir, file)
            name = os.path.basename(file)
            try:
                st = os.stat(path)
            except OSError:
                continue
            if dir == self_tags_dir:
                # 本插件自己的词典：直接用文件名作 key。
                # 不硬编码插件目录名，插件被改名/移动后旧 key 依然可用。
                key = name
            else:
                # 外部词典（TagComplete）：用相对 WebUI 根目录的路径作 key
                key = path.replace(base_dir, '')
            csvs.append({
                'key': key,
                'name': name,
                'size': st.st_size,
                # 毫秒级修改时间：前端据此判断词典是否被外部增改
                'mtime': int(st.st_mtime_ns // 1000000),
                'path': path
            })
    return csvs


def get_csv(key):
    """把前端传来的 key 解析为实际文件路径。

    优先级规则：只要 sd-webui-prompt-all-in-one-forge_en_zh_dictionary.csv 存在，任何指向回退词典
    （danbooru.zh_CN_SFW.csv）的请求都会被重定向到它；
    sd-webui-prompt-all-in-one-forge_en_zh_dictionary.csv 缺失时才使用回退词典。
    """
    name = _basename(key)

    if name == PREFERRED_DICT:
        return preferred_dict_path() or fallback_dict_path()

    if name == FALLBACK_DICT:
        preferred = preferred_dict_path()
        if preferred:
            return preferred

    # 常规解析：先按「WebUI 根目录 + key」，再退回本插件 tags/ 下的同名文件
    path = base_dir + str(key or '')
    if os.path.exists(path):
        return path
    path = os.path.join(self_tags_dir, name)
    if os.path.exists(path):
        return path
    return None
