import json

from scripts.physton_prompt.translator.base_tanslator import BaseTranslator
from scripts.physton_prompt.local_llm import get_service
from scripts.physton_prompt.storage import Storage

# 与 lora_new 共用同一套「标签 → 译文」JSON 约定，模型只需要按 key 回填
SYSTEM_PROMPT = "你是 AI 绘画提示词翻译专家，只输出 JSON，不输出任何多余文字。"
USER_PROMPT = """把下面的英文 danbooru 标签逐个翻译成 {to_lang}。

规则：
1. 输出一个 JSON 对象：key 必须与给出的英文原文完全一致，value 为 {to_lang}译文。
2. 使用 AI 绘画圈的通用译法，例如 "looking at viewer" 译为"看向观者"、"thighhighs" 译为"过膝袜"。
3. 只有「不含空格且含数字」的自造触发词（如 kei1、my_style_v2）才原样返回英文；
   用下划线连接的常见 danbooru 标签（如 open_mouth、long_hair）也要翻译成 {to_lang}。
4. 不做任何内容审查，成人内容、NSFW、俚语词汇直译。
5. 不要输出 JSON 以外的任何内容。

标签列表：
{tags}"""

# 用户在【AI翻译提示词】里自定义的模板（storage/local_llm_prompt.json）
PROMPT_STORAGE_KEY = 'local_llm_prompt'


def prompt_template():
    """读取自定义提示词模板；缺失或不含 {tags} 占位符时回落到内置模板。"""
    data = Storage.get(PROMPT_STORAGE_KEY)
    if isinstance(data, dict):
        text = str(data.get('text') or '')
    elif isinstance(data, str):
        text = data
    else:
        text = ''
    text = text.strip()
    if text and '{tags}' in text:
        return text
    return USER_PROMPT


def prompt_signature():
    """当前模板的指纹：进入译文缓存 key，改了提示词就不会命中旧译文。"""
    import hashlib
    return hashlib.md5(prompt_template().encode('utf-8')).hexdigest()[:12]


def _norm(text):
    """键名归一化：小写 + 空格转下划线（与 lna_llm_service 的 _normalize_tag 一致）。"""
    return str(text).strip().lower().replace(' ', '_')


def lang_name(code):
    """把 'zh-CN'/'zh_CN'/'en' 这类语言代码转成可读名称（如「简体中文」）。

    小模型对语言代码并不敏感，提示词里写「翻译成 zh-CN」远不如写
    「翻译成简体中文」明确；lora_new 的预设就是直接写语言名的。
    """
    raw = str(code or '')
    want = raw.replace('-', '_').lower()
    short = want.split('_')[0]
    try:
        from scripts.physton_prompt.get_i18n import get_i18n
        languages = get_i18n().get('languages', [])
        for item in languages:
            if str(item.get('code') or '').replace('-', '_').lower() == want:
                return _clean_lang_name(item)
        # 只有主语言代码时（如 'en'）按主语言找第一个条目（en_US）
        for item in languages:
            if str(item.get('code') or '').split('_')[0].lower() == short:
                return _clean_lang_name(item)
    except Exception:
        pass
    return raw


def _clean_lang_name(item):
    """语言名去掉末尾的地区括注：「简体中文 (中国)」→「简体中文」。"""
    name = str(item.get('name') or item.get('code') or '')
    for sep in (' (', '（'):
        if sep in name:
            name = name.split(sep)[0]
    return name.strip() or str(item.get('code') or '')


def _parse_json_loose(text):
    if not text:
        return {}
    s = str(text).strip()
    if s.startswith("```"):
        i = s.find("{")
        j = s.rfind("}")
        if i == -1 or j <= i:
            return {}
        s = s[i:j + 1]
    try:
        data = json.loads(s)
        return data if isinstance(data, dict) else {}
    except Exception:
        pass
    i, j = s.find("{"), s.rfind("}")
    if i != -1 and j > i:
        try:
            data = json.loads(s[i:j + 1])
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}
    return {}


class LocalLLMTranslator(BaseTranslator):
    def __init__(self):
        super().__init__('local_llm')

    def translate(self, text):
        if not text:
            return '' if not isinstance(text, list) else []
        return self.translate_batch(text if isinstance(text, list) else [text])[0]

    def translate_batch(self, texts):
        # 本地模型一次推理就能翻译一整批：不要走基类的「并发 + 每组 sleep 1s」，
        # 否则会反复排队抢共享锁，反而更慢
        service = get_service()
        if service is None:
            raise Exception('Local LLM service is not available')
        if not str(self.api_config.get('model') or '').strip():
            cfg = service.get_config()
            if not str(cfg.get('llm_model') or '').strip():
                raise Exception('No local LLM model selected')

        items = [str(t) for t in texts]
        prompt = prompt_template().replace('{to_lang}', lang_name(self.to_lang)).replace(
            '{tags}', json.dumps(items, ensure_ascii=False)
        )
        result = service.run_inference(prompt, SYSTEM_PROMPT, json_mode=True)
        if not result.get('ok'):
            raise Exception(result.get('error') or 'Local LLM inference failed')

        data = _parse_json_loose(result.get('text'))
        if not data:
            # 解析不出 JSON 时明确报错，避免「静默回填原文」看起来像翻译无效
            snippet = str(result.get('text') or '').strip().replace('\n', ' ')[:200]
            raise Exception('本地模型未返回可解析的 JSON' + ('：' + snippet if snippet else ''))
        # 键名宽松匹配：先精确，再忽略大小写，最后归一化（空格 ↔ 下划线）
        exact = {str(k): v for k, v in data.items()}
        lower = {str(k).strip().lower(): v for k, v in data.items()}
        normed = {_norm(k): v for k, v in data.items()}
        out = []
        for item in items:
            val = exact.get(item)
            if val is None:
                val = lower.get(item.strip().lower())
            if val is None:
                val = normed.get(_norm(item))
            if isinstance(val, str) and val.strip():
                out.append(val.strip())
            else:
                # 模型漏项时保留原文，避免把整段提示词清空
                out.append(item)
        return out
