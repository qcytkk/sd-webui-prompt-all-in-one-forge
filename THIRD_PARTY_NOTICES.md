# 第三方组件声明 / Third-Party Notices

本项目（`sd-webui-prompt-all-in-one-forge`）整体以 **MIT License** 发布，
但包含下列第三方代码，其授权条款独立于本项目，**不受 MIT 约束**。

This project is distributed under the **MIT License** as a whole, but bundles the
third-party component listed below. That component is licensed separately and is
**NOT** covered by the MIT License.

---

## 1. translators（`scripts/physton_prompt/translators/`）

| 项目 | 说明 |
|---|---|
| 名称 | translators |
| 作者 | UlionTse |
| 上游 | https://github.com/UlionTse/translators |
| 许可 | **GNU General Public License v3.0**（全文见 `LICENSE-GPL-3.0.txt`） |
| 本项目内的位置 | `scripts/physton_prompt/translators/server.py`（单文件分发，305 KB） |
| 调用方 | `scripts/physton_prompt/translator/translators_translator.py` |

该文件保留了原始版权头（`Copyright (C) 2017 UlionTse`）与 GPL-3.0 声明，未作删改。

### 为何是 GPL-3.0

`translators` 上游采用 GPL-3.0（强 copyleft）。按 GPL-3.0 要求：
- 分发时必须附带完整许可全文 → 见同目录 `LICENSE-GPL-3.0.txt`
- 必须保留原作者版权声明 → 已保留在该文件头部
- 必须提供对应源码 → 本仓库即包含完整源码

### 对本项目许可的影响（务必阅读）

由于上述目录包含 GPL-3.0 代码，**严格意义上**：
- 仅 MIT 声明不能覆盖整个仓库；
- 分发包含该目录的完整项目时，就整体而言需满足 GPL-3.0 的约束（GPL 的传染性）。

本项目的处理方式：**如实标注、分区说明，不隐藏该依赖**。

如果下游使用者需要一份**纯 MIT** 的副本，可以不包含
`scripts/physton_prompt/translators/` 目录，并改用 PyPI 上的 `translators`
包（`pip install translators`）—— 但需自行适配本插件对该模块的调用方式
（本项目使用的 `translate_text(reset_host_url=..., if_check_reset_host_url=...)`
参数为上游对原库的定制改动，PyPI 版本未必兼容）。

### 上游来源说明

该文件同样存在于本项目的上游插件
[Physton/sd-webui-prompt-all-in-one](https://github.com/Physton/sd-webui-prompt-all-in-one)，
本项目沿用上游的分发方式。

---

## 2. 其它依赖

前端依赖（Vue、axios、js-yaml、papaparse、sortablejs、tinycolor2、tippy.js、
toastr、vue-clipboard3、vue3-colorpicker 等）通过 `src/package.json` 声明，
按其各自许可使用，未以源码形式纳入本仓库。

后端 Python 依赖（`openai`、`boto3`、`aliyun-python-sdk-*`、`chardet`、`fastapi`、
`PyExecJS`、`lxml`、`tqdm`、`pathos`、`cryptography`）通过 `install.py` 在运行时安装，
未以源码形式纳入本仓库。
