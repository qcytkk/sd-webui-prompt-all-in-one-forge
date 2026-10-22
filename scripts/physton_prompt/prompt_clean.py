"""把大模型返回的「提示词生成」结果清洗成一行可用的 SD 标签串。

背景：小参数模型（或带思考过程的模型）经常输出
「用户描述了…我需要生成…生成提示词：<标签串>」这类内容，
甚至会在标签串末尾无休止地重复同一个标签。直接拿去填写提示词框不可用。

清洗策略（不依赖模型，纯粹后处理）：
1. 去掉 Markdown 代码块围栏
2. 按行评分，挑出「合法标签最多」的一行（推理段落里的中文行得分为 0，自然被丢弃）
3. 逗号切分 → 小写 → 下划线转空格 → 去引号/空白 → 丢弃含中文或过长的项
4. 去重（保留首次出现顺序）
5. 连续重复 3 次视为模型退化，到此截断
6. 标签总数上限 60

返回清洗后的一行标签；若清洗不出任何合法标签，返回原文本（便于用户自行判断）。
"""

import re

MAX_TAGS = 60
MAX_TAG_WORDS = 6

# 允许出现在标签里的字符：英文、数字、空格与常见符号
_TAG_CHARS = re.compile(r"^[a-zA-Z0-9 ()\[\]{}<>:.\-_,&+'/!?@#$%*~|\\=]+$")
# 中日韩字符（出现即判定为自然语言说明，不是标签）
_CJK = re.compile(r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uac00-\ud7af]")
# 行首常见前缀，如「生成提示词：」「Prompt:」
_PREFIX = re.compile(
    r"^\s*(?:最终的?|生成的?|输出|结果)?\s*(?:提示词|prompts?|tags?|标签)\s*[:：]\s*",
    re.IGNORECASE,
)


def _clean_tag(tag):
    tag = str(tag or "").strip()
    tag = tag.strip("\"'`“”‘’")          # 去掉包裹引号
    tag = tag.replace("_", " ")            # danbooru 下划线 → 空格
    tag = re.sub(r"\s+", " ", tag).strip()
    tag = tag.strip(",.;。；，")
    if not tag:
        return ""
    if _CJK.search(tag):                   # 含中文 → 说明文字，不是标签
        return ""
    if not _TAG_CHARS.match(tag):          # 含奇怪符号（如 emoji）→ 丢弃
        return ""
    if len(tag.split(" ")) > MAX_TAG_WORDS:
        return ""
    return tag.lower()


def _line_score(line):
    """一行里有多少个合法标签：用来挑出真正的答案行。"""
    raw = _PREFIX.sub("", line)
    parts = re.split(r"[,，;；]", raw)
    return sum(1 for p in parts if _clean_tag(p))


def _pick_best_line(text):
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if not lines:
        return ""
    best_line, best_score = "", -1
    for line in lines:
        score = _line_score(line)
        # 得分相同时取靠后的行（模型通常把结论放在推理之后）
        if score >= best_score:
            best_line, best_score = line, score
    return best_line if best_score > 0 else ""


def sanitize_tags(text):
    if not text:
        return ""
    raw = str(text)
    # 去代码块围栏
    raw = re.sub(r"```[a-zA-Z0-9_-]*", "", raw).replace("```", "")

    line = _pick_best_line(raw)
    if not line:
        # 没有明显答案行：退化成整段参与切分（单行输出的情况）
        line = raw

    line = _PREFIX.sub("", line)
    parts = re.split(r"[,，;；\n]", line)

    result = []
    seen = set()
    repeat_count = 1
    prev = ""
    for part in parts:
        tag = _clean_tag(part)
        if not tag:
            continue
        if tag == prev:
            repeat_count += 1
            # 连续重复 3 次 → 模型已进入退化循环，直接截断
            if repeat_count >= 3:
                break
            continue
        repeat_count = 1
        prev = tag
        if tag in seen:
            continue
        seen.add(tag)
        result.append(tag)
        if len(result) >= MAX_TAGS:
            break

    if not result:
        return str(text).strip()
    return ", ".join(result)
