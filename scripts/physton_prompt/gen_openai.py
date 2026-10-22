from scripts.physton_prompt.get_lang import get_lang
from scripts.physton_prompt.get_translate_apis import unprotected_translate_api_config
from scripts.physton_prompt.prompt_clean import sanitize_tags


def gen_openai(messages, api_config):
    import openai
    from distutils.version import LooseVersion
    api_config = unprotected_translate_api_config('chatgpt_key', api_config)
    openai.api_base = api_config.get('api_base', 'https://api.openai.com/v1')
    openai.api_key = api_config.get('api_key', '')
    model = api_config.get('model', 'gpt-3.5-turbo')
    if not openai.api_key:
        raise Exception(get_lang('is_required', {'0': 'API Key'}))
    if not messages or len(messages) == 0:
        raise Exception(get_lang('is_required', {'0': 'messages'}))
    # max_tokens 限制输出长度：避免模型进入「标签无限重复」的退化循环
    if LooseVersion(openai.__version__) < LooseVersion('1.0.0'):
        completion = openai.ChatCompletion.create(
            model=model, messages=messages, timeout=60, max_tokens=400
        )
    else:
        from openai import OpenAI
        client = OpenAI(
            base_url=openai.api_base,
            api_key=openai.api_key,
        )
        completion = client.chat.completions.create(
            model=model, messages=messages, timeout=60, max_tokens=400
        )
    if len(completion.choices) == 0:
        raise Exception(get_lang('no_response_from', {'0': 'OpenAI'}))
    content = completion.choices[0].message.content
    # 统一清洗：去掉推理过程/前缀/代码块/重复标签，只留一行合法标签
    return sanitize_tags(content)
