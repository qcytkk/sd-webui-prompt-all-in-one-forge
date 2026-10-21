"""【本地ai大模型翻译】的 HTTP 路由（挂在 /physton_prompt/local_llm/* 下）。

模型目录、运行环境、llama.cpp 实例、推理锁与空闲卸载线程全部来自
`sd_forge_lora_new/lna_llm_service`，本文件只做参数转发与错误文案翻译。
"""
import os
import subprocess
import sys

from fastapi import Request
from fastapi.concurrency import run_in_threadpool

from scripts.physton_prompt import local_llm
from scripts.physton_prompt.storage import Storage

# 共享服务返回的英文短标识 → 本插件语言包里的键
_ERR_KEYS = {
    'Invalid model path': 'llm_invalid_model_path',
    'cpuBuildNoGpu': 'llm_no_cuda_build',
    'Invalid repo': 'llm_invalid_repo',
    'Invalid filename': 'llm_invalid_filename',
    'Download busy': 'llm_download_busy',
}
_MIN_CUDA_DRIVER = (527, 41)


def _t(key, **vars):
    from scripts.physton_prompt.get_lang import get_lang
    text = get_lang(key)
    for k, v in vars.items():
        text = text.replace('{' + k + '}', str(v))
    return text


def _err(msg):
    msg = str(msg or '')
    key = _ERR_KEYS.get(msg)
    return _t(key) if key else msg


def _disabled():
    return {'ok': False, 'error': _t('llm_not_enabled_plugin')}


def _owner():
    return local_llm.owner()


def _open_in_explorer(folder):
    try:
        if os.name == 'nt':
            os.startfile(str(folder))
        else:
            opener = 'open' if sys.platform == 'darwin' else 'xdg-open'
            subprocess.Popen([opener, str(folder)])
    except Exception as e:
        return str(e)
    return ''


def register(app):
    @app.get('/physton_prompt/local_llm/status')
    async def _llm_status():
        return await run_in_threadpool(local_llm.status)

    @app.get('/physton_prompt/local_llm/models')
    async def _llm_models():
        service = local_llm.get_service()
        if service is None:
            return _disabled()
        # 引擎探测走子进程，不在本进程 import llama_cpp
        probe = await run_in_threadpool(service.probe_runtime)
        st = await run_in_threadpool(local_llm.status)
        return {
            'ok': True,
            'models': service.scan_models(),
            'selected': st.get('selected', ''),
            'engine_ready': bool(probe.get('usable')),
            'engine_error': str(probe.get('error') or ''),
            'cuda_available': probe.get('build') == 'cuda',
            'gpu': bool(st.get('gpu')),
            'loaded': st.get('model', ''),
            'frozen': local_llm.frozen(),
            'dir': str(service.llm_dir()),
        }

    @app.post('/physton_prompt/local_llm/select')
    async def _llm_select(request: Request):
        service = local_llm.get_service()
        if service is None:
            return _disabled()
        data = await request.json()
        res = await run_in_threadpool(
            service.select_model, str(data.get('rel') or ''), 'prompt'
        )
        if not res.get('ok'):
            return {'ok': False, 'error': _err(res.get('error'))}
        return {'ok': True, 'selected': res.get('selected', '')}

    @app.post('/physton_prompt/local_llm/gpu')
    async def _llm_gpu(request: Request):
        service = local_llm.get_service()
        if service is None:
            return _disabled()
        data = await request.json()
        res = await run_in_threadpool(service.set_gpu, bool(data.get('gpu')), 'prompt')
        if not res.get('ok'):
            return {'ok': False, 'error': _err(res.get('error'))}
        return {'ok': True, 'gpu': bool(res.get('gpu'))}

    @app.post('/physton_prompt/local_llm/unload')
    async def _llm_unload():
        service = local_llm.get_service()
        if service is None:
            return _disabled()
        # 手动卸载不冻结：模型实例是共享的，卸载对两个插件都安全；
        # 只有「空闲自动卸载」的配置归属 lora_new（见 idle_settings）。
        unloaded = await run_in_threadpool(service.unload)
        return {'ok': True, 'unloaded': bool(unloaded), **(await run_in_threadpool(local_llm.status))}

    @app.post('/physton_prompt/local_llm/idle_settings')
    async def _llm_idle_settings(request: Request):
        service = local_llm.get_service()
        if service is None:
            return _disabled()
        if local_llm.frozen():
            return {'ok': False, 'error': _t('llm_unload_frozen')}
        data = await request.json()
        await run_in_threadpool(
            service.set_idle_settings,
            bool(data['auto_unload']) if 'auto_unload' in data else None,
            data.get('minutes') if 'minutes' in data else None,
            'prompt',
        )
        return await run_in_threadpool(local_llm.status)

    @app.get('/physton_prompt/local_llm/prompt')
    async def _llm_prompt():
        service = local_llm.get_service()
        if service is None:
            return _disabled()
        from scripts.physton_prompt.translator.local_llm_translator import USER_PROMPT, prompt_template
        return {
            'ok': True,
            'text': await run_in_threadpool(prompt_template),
            'default': USER_PROMPT,
            'key': '{tags}',
            'max': 4000,
        }

    @app.post('/physton_prompt/local_llm/prompt')
    async def _llm_prompt_save(request: Request):
        service = local_llm.get_service()
        if service is None:
            return _disabled()
        data = await request.json()
        text = str(data.get('text') or '')
        from scripts.physton_prompt.translator.local_llm_translator import (
            PROMPT_STORAGE_KEY, USER_PROMPT, prompt_template,
        )
        if not text.strip():
            # 清空即恢复内置模板
            Storage.delete(PROMPT_STORAGE_KEY)
            return {'ok': True, 'text': USER_PROMPT}
        if '{tags}' not in text:
            return {'ok': False, 'error': _t('llm_prompt_need_tags')}
        if len(text) > 4000:
            return {'ok': False, 'error': _t('llm_prompt_too_long')}
        Storage.set(PROMPT_STORAGE_KEY, {'text': text})
        return {'ok': True, 'text': await run_in_threadpool(prompt_template)}

    @app.post('/physton_prompt/local_llm/open_folder')
    async def _llm_open_folder():
        service = local_llm.get_service()
        if service is None:
            return _disabled()
        folder = service.llm_dir()
        try:
            folder.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            return {'ok': False, 'error': str(e)}
        err = await run_in_threadpool(_open_in_explorer, folder)
        if err:
            return {'ok': False, 'error': err}
        return {'ok': True, 'path': str(folder)}

    @app.post('/physton_prompt/local_llm/repo_files')
    async def _llm_repo_files(request: Request):
        service = local_llm.get_service()
        if service is None:
            return _disabled()
        data = await request.json()
        res = await run_in_threadpool(service.repo_files, str(data.get('repo') or ''))
        if not res.get('ok'):
            return {'ok': False, 'error': _err(res.get('error'))}
        return res

    @app.post('/physton_prompt/local_llm/download')
    async def _llm_download(request: Request):
        service = local_llm.get_service()
        if service is None:
            return _disabled()
        data = await request.json()
        res = await run_in_threadpool(
            service.start_download, str(data.get('repo') or ''), str(data.get('filename') or '')
        )
        if not res.get('ok'):
            return {'ok': False, 'error': _err(res.get('error'))}
        return res

    @app.get('/physton_prompt/local_llm/download_status')
    async def _llm_download_status():
        service = local_llm.get_service()
        if service is None:
            return _disabled()
        return {'ok': True, **(await run_in_threadpool(service.download_status))}

    @app.get('/physton_prompt/local_llm/runtime_info')
    async def _llm_runtime_info(force: bool = False):
        service = local_llm.get_service()
        if service is None:
            return _disabled()
        return await run_in_threadpool(service.runtime_info, bool(force))

    @app.post('/physton_prompt/local_llm/runtime_download_cuda')
    async def _llm_runtime_download_cuda():
        service = local_llm.get_service()
        if service is None:
            return _disabled()
        res = await run_in_threadpool(service.start_cuda_download)
        if not res.get('ok'):
            msg = str(res.get('error') or '')
            if msg == 'No NVIDIA GPU':
                return {'ok': False, 'error': _t(
                    'llm_no_nvidia', min='.'.join(str(x) for x in _MIN_CUDA_DRIVER),
                    hint=res.get('driver') or '',
                )}
            return {'ok': False, 'error': _err(msg)}
        return res

    @app.post('/physton_prompt/local_llm/gen')
    async def _llm_gen(request: Request):
        # 【使用Ai生成提示词】走本地模型时的推理入口：system = 预设，user = 图片描述
        from scripts.physton_prompt import local_llm
        if local_llm.get_service() is None:
            return {'success': False, 'message': _t('llm_not_enabled_plugin')}
        data = await request.json()
        messages = data.get('messages') or []
        if not messages:
            return {'success': False, 'message': _t('is_required', **{'0': 'messages'})}
        system_prompt = ''
        user_parts = []
        for item in messages:
            content = str((item or {}).get('content') or '')
            if (item or {}).get('role') == 'system' and not system_prompt:
                system_prompt = content
            elif content:
                user_parts.append(content)
        res = await run_in_threadpool(
            local_llm.run_inference, '\n\n'.join(user_parts), system_prompt
        )
        if not res.get('ok'):
            return {'success': False, 'message': res.get('error') or 'Local LLM inference failed'}
        return {'success': True, 'result': str(res.get('text') or '').strip()}

    @app.get('/physton_prompt/local_llm/runtime_download_status')
    async def _llm_runtime_download_status():
        service = local_llm.get_service()
        if service is None:
            return _disabled()
        st = await run_in_threadpool(service.runtime_download_status)
        return {
            'ok': True,
            'active': st['active'],
            'done': st['done'],
            'total': st['total'],
            'attempt': st['attempt'],
            'error': st['error'],
            'finished': st['ok'],
            'cuda_wheel_ready': st['cuda_wheel_ready'],
        }
