# sd-webui-prompt-all-in-one-forge

> **本项目是二次开发版**，基于 [Physton/sd-webui-prompt-all-in-one](https://github.com/Physton/sd-webui-prompt-all-in-one) 修改而来。
> 原项目采用 MIT License（Copyright © 2023 Physton），本仓库保留其完整许可与署名。

Stable Diffusion WebUI / Forge 的提示词输入增强扩展：标签翻译、补全、历史记录、收藏、
以及基于大模型的提示词生成。

---

## 与原版的差异

| 方面 | 说明 |
|---|---|
| **界面** | 全部弹窗按统一设计规范重做（令牌化配色、亮/暗双主题、模态化、键盘无障碍） |
| **交互** | 多个弹窗从「自动关闭/悬浮层」改为显式关闭的模态；保存行为统一 |
| **本地翻译** | **移除原版的离线翻译模型**（mbart50 等），改用 **llama.cpp** 本地推理 |
| **提示词生成** | 新增【使用 Ai 生成提示词】：支持**本地模型**或**任意 OpenAI 兼容 API** |
| **AI 精翻** | 中文词典增加 AI 精翻（本地大模型或 API） |
| **翻译缓存** | 新增翻译缓存，缓存联网翻译与 AI 翻译结果，避免重复翻译浪费时间 |
| **模型共享** | 本地模型与 [sd_forge_lora_new](https://github.com/qcytkk/sd_forge_lora_new) 共用同一引擎 |

---

## 功能

- 提示词 / 反向词输入框增强：标签高亮、权重调整、拖拽排序、分组标签面板
- 翻译：关键词组词典 → CSV 词典 → 联网翻译接口 → 本地 AI 大模型（依次回退）
- 机翻词典缓存：联网与 AI 翻译结果落盘复用
- 历史记录 / 收藏列表
- 【使用 Ai 生成提示词】：上传画面描述 → 生成英文 SD 提示词（本地模型 / OpenAI 兼容 API 可选）
- 多语言界面（108 种语言）

---

## 安装

### 前置：本插件

```bash
cd <WebUI 根目录>/extensions
git clone https://github.com/qcytkk/sd-webui-prompt-all-in-one-forge.git
```

重启 WebUI。首次启动时 `install.py` 会自动安装 Python 依赖
（`openai`、`boto3`、`aliyun-python-sdk-*`、`chardet`、`fastapi`、`PyExecJS`、
`lxml`、`tqdm`、`pathos`、`cryptography`）。

### 可选：本地 AI 模型（本地翻译 / 本地提示词生成）

本地模型能力**依赖联动插件** [sd_forge_lora_new](https://github.com/qcytkk/sd_forge_lora_new)：

```bash
cd <WebUI 根目录>/extensions
git clone https://github.com/qcytkk/sd_forge_lora_new.git
```

- 两个插件**共用同一个 llama.cpp 实例、同一把推理锁、同一套空闲卸载逻辑**
- **没有 `sd_forge_lora_new` 时，本地 AI 的翻译与提示词生成不可用**
  （联网翻译、CSV 词典、API 生成仍然可用）

模型文件放在 `models/LLM/` 下（`.gguf`），可在
【插件设置 → 翻译设置 → 本地AI大模型翻译】中选择与加载。

---

## 使用要点

### 翻译流程

在【插件设置 → 翻译设置】中可调整四档翻译源的**启用状态与先后顺序**：

```
关键词组（yaml） → 标签词典（CSV） → 机翻词典（缓存） → 联网翻译 / 本地AI
```

未命中的词条会继续往下一档传递，逐级回退。

### 使用 Ai 生成提示词

1. 正向提示词框工具栏点击 ChatGPT 图标（可在【插件设置 → 通用设置】隐藏该按钮）
2. 在【选用ai模型】中选择来源：
   - **本地模型**：显示 `models/LLM` 中当前选中的模型名
   - **API 模型**：显示 API 配置中的【模型名称】
3. 填写画面描述 → 点【生成】→ 结果可一键应用到提示词框

API 配置支持任意 OpenAI 兼容服务；本地部署的服务通常填
`API 地址 = http://127.0.0.1:<端口>/v1`、`API Key = sk-local`。

---

## 目录结构

```
├── install.py                     # 扩展入口：安装 Python 依赖
├── scripts/
│   ├── on_app_started.py          # 注册全部 /physton_prompt/* 路由
│   └── physton_prompt/            # 后端模块
│       ├── translate.py           # 翻译调度（四档回退）
│       ├── csv.py                 # CSV 词典
│       ├── local_llm.py           # 本地模型服务桥接
│       ├── local_llm_api.py       # 本地模型 HTTP 路由
│       ├── machine_dict.py        # 机翻词典缓存
│       ├── translator/            # 各翻译引擎实现
│       └── translators/           # 第三方 translators 库（GPL-3.0，见下方声明）
├── src/                           # 前端工程（Vue 3 + Vite）
├── javascript/main.entry.js       # 前端构建产物（WebUI 实际加载）
├── style.css                      # 全局样式（WebUI 自动加载）
├── i18n.json                      # 界面文案（108 语言）
├── translate_apis.json            # 翻译接口目录
├── tags/                          # 中英词典 CSV
└── group_tags/                    # 标签分组面板（各语言 yaml）
```

---

## 开发

前端改动需要重新构建：

```bash
cd src
npm install
npx vite build
```

构建产物为 `javascript/main.entry.js`，由 WebUI 加载。

⚠️ Forge 会把扩展 JS/CSS 以 `?<文件mtime>` 注入页面，该 mtime 只在启动或
「设置 → Actions → Reload custom script bodies」时刷新。因此：

- 改前端产物或 `style.css`：**Reload custom script bodies → 刷新页面**
- 改后端 Python：**重启 WebUI**
- 改 `i18n.json` / `translate_apis.json` / `tags/` / `group_tags/`：**刷新页面即可**

---

## 许可

本项目以 **MIT License** 发布，完整文本见 [LICENSE](LICENSE)。

- 原始版权：`Copyright (c) 2023 Physton`（[原项目](https://github.com/Physton/sd-webui-prompt-all-in-one)）
- 本仓库的修改：`Copyright (c) 2026 qcytkk`

⚠️ **例外**：`scripts/physton_prompt/translators/` 内含
[UlionTse/translators](https://github.com/UlionTse/translators) 的代码，
其许可为 **GNU GPL-3.0**，**不受本项目 MIT 条款约束**。
详见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

---

## 致谢

- [Physton/sd-webui-prompt-all-in-one](https://github.com/Physton/sd-webui-prompt-all-in-one) —— 原项目
- [UlionTse/translators](https://github.com/UlionTse/translators) —— 多引擎翻译库
- [DominikDoom/a1111-sd-webui-tagcomplete](https://github.com/DominikDoom/a1111-sd-webui-tagcomplete) —— 标签补全词典格式
