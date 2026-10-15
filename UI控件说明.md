# sd-webui-prompt-all-in-one-forge · 界面控件说明

> **用途**：本插件这一端没有"浏览器元素选择器"，此文件用于**用文字精确指认界面上的按钮 / 图标 / 控件**，供人类与 AI 助手（WorkBuddy 等）沟通改动需求。
>
> **指认方式（推荐格式）**：`区域 → 控件文案 → 类型`，例如：
> 「设置弹窗 / 左侧标签栏 / 【通用设置】」、「主界面 / 顶部图标栏 / 【设置】齿轮图标」、「主界面 / 标签扩展面板 / 【添加权重：叠加()】按钮」。
>
> **文案来源**：所有界面文字都来自根目录 `i18n.json` 的 `zh_CN`，下面每条都给出对应 **key**（形如 `getLang('xxx')`），改文案即改 `i18n.json`（改完刷新页面即生效，无需重启/重建）。
>
> **图标**：绝大多数图标由 `<icon-svg name="xxx">` 渲染成 `<div class="icon-svg icon-svg-xxx">`，图形文件在 `styles/icons/xxx.svg`。指认图标时直接说 **图标名** 最精确。
>
> 最后更新：2026-10-16

---

## 0. 总体结构

- **主界面**：`src/src/App.vue` 会为 **4 个提示词输入框**各注入一份 `physton-prompt`（文生图·正面 / 文生图·负面 / 图生图·正面 / 图生图·负面），插入位置在**各输入框所在区块的正后方**。
- **主组件**：`src/src/components/phystonPrompt.vue`（含 4 个 mixin：`headerMixin` / `tagMixin` / `groupTagsMixin` / `dropMixin`）。
- **弹窗组件**：`settingsModal.vue`（设置，多标签页）+ 其内嵌的 `translateSetting / promptFormat / blacklist / hotkey / extensionCss / about`；以及 `selectLanguage`、`history`、`favorite`、`chatgptPrompt`、`extraNetworksPopup`、`packagesState`（+ `App.vue` 内的粘贴弹窗、`highlightPrompt` 高亮层）。
- **构建产物**：`javascript/main.entry.js`（**改 `src/` 下任何文件都必须重建**，见 `项目开发说明.md` §4）。
- **样式**：根目录 `style.css`（WebUI 框架自动加载，不参与构建）；上游视觉体系在 `styles/main.less` / `styles/main.min.css`。

---

## 1. 主界面（每个提示词框都有一份）

### 1.1 标题栏（`.prompt-header`）

| 控件 | 可见文案 | 类型 | CSS 类名 | 源文件 | 行为 |
|---|---|---|---|---|---|
| 折叠/展开手柄 | 显示面板 / 隐藏面板（`show_panel` / `hide_panel`） | 图标按钮 `unfold` | `.prompt-unfold` | phystonPrompt.vue:5 | 折叠/展开整个面板 |
| 标题 | 提示词（`prompt`）/ 反向词（`negative_prompt`） | 文本 | `.prompt-header-title` | :8 | 只读 |
| token 计数 | `(12/75)` | 文本 | `.prompt-header-counter` | :9 | 只读（由 `/token_counter` 返回） |

### 1.2 顶部图标按钮栏（一排小图标，`.extend-btn-item`）

> 每份提示词框都有一排；顺序如下（`phystonPrompt.vue:10-101`）。**正面框比负面框多一个 ChatGPT 按钮**。

| # | 图标名 | 悬停提示（zh_CN） | key | 行为 |
|---|---|---|---|---|
| 1 | `setting` | 设置：翻译API、自动翻译、显示/隐藏... | `setting_desc` | **打开设置弹窗**（`settingsModal.vue`） |
| 2 | `history` | 历史记录 | `history` | 打开**历史记录浮层**（`history.vue`） |
| 3 | `favorite` | 收藏列表 | `favorite` | 打开**收藏列表浮层**（`favorite.vue`） |
| 4 | `translate` | 一键翻译所有关键词（`one_translate_all_keywords`）／ 翻译关键词到本地语言（`translate_keywords_to_local_language`） | 同左 | 翻译全部标签 → 本地语言（翻译中变 `loading` 图标） |
| 5 | `english` | 翻译所有非英文的关键词到英文 | `translate_all_keywords_to_english` | 翻译全部标签 → 英文。**仅当语言非"可一键翻译"时才出现**（与 #4 二选一） |
| 6 | `copy` | 复制所有关键词到剪贴板 | `copy_keywords_to_clipboard` | 复制当前所有标签 |
| 7 | `remove` | 删除所有关键词 | `delete_all_keywords` | 清空全部标签（有确认弹窗） |
| 8 | `load2` | 加载WebUI提示词 | `load_webui_prompt` | 手动从 WebUI 输入框加载。**仅当"自动加载"关闭时出现** |
| 9 | `chatgpt` | 使用ChatGPT生成Prompt | `use_chatgpt_gen_prompts` | 打开 **ChatGPT 弹窗**。**仅正面框出现** |

> 注：原 #1 `i18n`（Language 按钮）已于 2026-10-16 移除，功能迁入【设置弹窗 → 通用设置 → 界面语言】下拉（见 §2.1 与 §2.2）。

### 1.3 输入区与两个开关（`.prompt-header-extend.prompt-append`，`phystonPrompt.vue:102-132`）

| 控件 | 可见文案 | key | 类型 | CSS 类名 |
|---|---|---|---|---|
| 自动加载开关 | 自动加载WebUI提示词变动。勾选后，当WebUI中提示词输入框的内容变动时，插件会自动加载关键词解析并格式化。未勾选，当WebUI中提示词输入框的内容变动时，需要手动点击加载提示词按钮。 | `auto_load_webui_prompt` | 复选框 `load` | `.gradio-checkbox` |
| 隐藏默认输入框 | 隐藏默认输入框 / 显示默认输入框 | `hide_default_input_box` / `show_default_input_box` | 复选框 `input` | `.gradio-checkbox` |
| 新增标签输入框 | 占位：请输入新关键词（`please_enter_new_keyword`）；提示：按回车键添加关键词（`enter_to_add`） | 同左 | 文本框 | `textarea.input-tag-append` |

**输入时的补全列表**（`.prompt-append-list`）：按类型分组（换行 `wrap` / 历史 `history` / 收藏 `favorite`），点分组名展开子项，点条目把该标签追加到当前提示词。

### 1.4 提示词标签区（`.prompt-tags`，`phystonPrompt.vue:184-325`）

| 控件 | 可见文案 | key | CSS 类名 | 行为 |
|---|---|---|---|---|
| 标签本体 | 提示：鼠标左键点击进行编辑 / 鼠标双击禁用启用关键词 / 鼠标左键按住拖动进行排序 | `click_to_edit` / `dblclick_to_disable` / `drop_to_order` | `.prompt-tag-value` | 点击/双击/右键的行为**由【快捷键设置】决定**（默认 左键=编辑、双击=禁用启用、悬停=显示扩展面板）；可拖动排序 |
| 删除单个标签 | — | — | `.btn-tag-delete`（图标 `close`） | 删除该标签 |
| 换行标签 | 换行符号 / 鼠标左键按住拖动进行排序 | `line_break_character` / `drop_to_order` | `.prompt-tag.wrap-tag` | 换行占位 |

**标签扩展面板**（`.btn-tag-extend`，悬停或按快捷键出现，`phystonPrompt.vue:247-307`）：

| 控件 | 可见文案 | key | 图标 |
|---|---|---|---|
| 权重数字框 | — | — | `.input-number`（`vue-number-input`，步进 0.1） |
| 增加权重：叠加() | 增加关键词权重：叠加() | `increase_weight_add_parentheses` | `weight-parentheses-inc`（NovelAI 符号时变 `weight-braces-inc`） |
| 增加权重：减少() | 增加关键词权重：减少() | `increase_weight_subtract_parentheses` | `weight-parentheses-dec` |
| 减弱权重：叠加[] | 减弱关键词权重：叠加[] | `decrease_weight_add_brackets` | `weight-brackets-inc` |
| 减弱权重：减少[] | 减弱关键词权重：减少[] | `decrease_weight_subtract_brackets` | `weight-brackets-dec` |
| 换行符号 | 换行符号 | `line_break_character` | `wrap` |
| 翻译为英文 | 翻译为英文 | `translate_keyword_to_english` | `english`（翻译中 `loading`） |
| 复制到剪贴板 | 复制到剪贴板 | `copy_to_clipboard` | `copy` |
| 收藏 | 添加到收藏 / 从收藏中移除 | `add_to_favorite` / `remove_from_favorite` | `favorite-no` / `favorite-yes` |
| 加入黑名单 | 添加到黑名单 | `add_blacklist` | `blacklist` |
| 禁用/启用 | 禁用关键词 / 启用关键词 | `disable_keyword` / `enable_keyword` | `disabled` / `enable` |

**标签的本地语言显示**（`.prompt-local-language`，非英文语言时）：左侧 `translate` 小图标（提示 翻译关键词到本地语言 `translate_keyword_to_local_language`），右侧 `.local-language` 显示译文。

### 1.5 批量操作（拖拽框选标签后出现，`phystonPrompt.vue:331-354`）

`.drop-select-btns`：标题「批量操作」（`batch_operation`），按钮依次为 **复制到剪贴板 / 添加到收藏 / 禁用关键词 / 启用关键词 / 删除**（图标 `copy` / `favorite-no` / `disabled` / `enable` / `remove`；最后一个是删除，无 tooltip）。

### 1.6 分组标签面板（`.group-tabs`，`phystonPrompt.vue:356-463`）

| 控件 | 可见文案 | key | CSS 类名 | 行为 |
|---|---|---|---|---|
| 显示/隐藏手柄 | 显示分组标签 / 隐藏分组标签 | `show_group_tags` / `hide_group_tags` | `.show-group-tags`（图标 `unfold`） | 折叠整个分组面板 |
| 一级分组页签 | 分组名（来自 `group_tags/*.yaml`，如"Webui / 收藏列表 / Extra Networks"） | — | `.group-tab` | 切换一级分组 |
| 二级分组页签 | 子分组名 | — | `.sub-group-tab` | 切换二级分组 |
| 标签条目 | 中文名 + 英文名（悬停翻译提示） | — | `.tag-item` / `.tag-local` / `.tag-en` | 点击把标签加入提示词 |
| 额外网络卡片 | 模型名 | — | `.group-extra-network`（`.extra-network-preview` / `.extra-network-name` / `.extra-network-loading`） | 点击加入 `<lora:...>` 等；悬停出信息浮层 |
| （extraNetworks 底部）刷新 | 刷新 | `refresh` | `.tags-size-item`（图标 `refresh` / `loading`） | 重新拉取额外网络 |
| （extraNetworks 底部）宽度 | 宽度 | `width` | `.size-number` + `.size-title` | 卡片宽度(10-1000) |
| （extraNetworks 底部）高度 | 高度 | `height` | `.size-number` + `.size-title` | 卡片高度(10-1000) |
| （普通分组底部）标签颜色 | 标签颜色: | `tags_color` | `.tags-color` + `.tags-color-picker`（颜色选择器） | 改该组标签颜色 |
| （普通分组底部）重置颜色 | 重置为默认颜色 | `reset_default_color` | `.tags-color-reset`（图标 `reset`） | 恢复默认色 |
| （普通分组底部）清除颜色 | 清除颜色 | `clear_color` | `.tags-color-clear`（图标 `clear`） | 清除自定义色 |
| （普通分组底部）版权 | 提示词整合来源 路过银河(知乎)、未知作者(Google Drive)、互联网等等，感谢这些作者的无私奉献！ | `tags-copyright` | `.tags-copyright` | 只读 |

---

## 2. 弹窗

### 2.1 设置弹窗（`settingsModal.vue`）

- **入口**：主界面顶部 `setting` 齿轮图标（提示 `setting_desc`）。
- **标题**：`setting_desc`（设置：翻译API、自动翻译、显示/隐藏...）。
- **右上角**：仅关闭按钮（图标 `close`）。**主题切换按钮已于 2026-10-16 移入【通用设置】内容区**（见下方「WebUI 主题」行）。
- **遮罩**：点击弹窗外部区域即关闭（`@click="onMaskClick"`）。

**左侧标签栏**（`.settings-modal-tabs` → `.settings-tab-item` → `.settings-tab-icon` + `.settings-tab-label`；定义在 `settingsModal.vue` 的 `tabs` 数组）：

| 顺序 | 标签文案（zh_CN） | key | 图标 | 内容区子组件 |
|---|---|---|---|---|
| 1 | 通用设置 | `setting` | `setting` | 本文件内联（见下） |
| 2 | 翻译接口 | `translate_api` | `api` | `translateSetting.vue` |
| 3 | Prompt格式 | `prompt_format` | `format` | `promptFormat.vue` |
| 4 | 关键词黑名单 | `keywords_blacklist` | `blacklist` | `blacklist.vue` |
| 5 | 快捷键设置 | `hotkey_setting` | `hotkey` | `hotkey.vue` |
| 6 | 插件样式扩展 | `theme_extension` | `theme` | `extensionCss.vue` |
| 7 | 关于、更新、帮助、文档 | `about_desc` | `about` | `about.vue` |

> 内容容器：`.settings-modal-content` / `.settings-tab-pane`；行样式 `.setting-line` + `.line-title` + `.line-content`。

**① 通用设置（`common`）**

> **分组结构**（`.settings-section` + `.settings-section-title`；组间有虚线、组内行间有虚线）：本页现有 **2 个带标题的分组** —— **提示与自动填充**（`tooltip_and_auto_input`：提示框开关 + 自动填充×2）、**自动翻译**（`auto_translation`）。原先的「外观」（`appearance`）分组标题已于 2026-10-16 按用户要求**去掉**（该组仅「界面语言 + WebUI 主题」两行，标题冗余）；`appearance` 键因此成为**死键**（未清理）。

| 控件 | 可见文案 | key | CSS 类名 | 行为 |
|---|---|---|---|---|
| 提示框总开关 | 是否启用每个功能的提示框，如果你已经熟练掌握本扩展的所有功能，可以取消勾选 | `whether_to_enable_tooltip` | `.setting-line` > `.gradio-checkbox`（图标 `tooltip`） | **标题在上、勾选框只留"图标+开关"**（2026-10-16 去重后） |
| 界面语言 | 界面语言 | `interface_language` | `.setting-line` > `select.language-select` | 下拉选界面语言（108 项，文案 `code - 名称`，选项来自 i18n.json 的 languages）。选中即切换（emit `update:languageCode`，App.vue watcher 落盘 + 重载分组标签）。**2026-10-16 由顶栏 i18n 按钮迁入** |
| WebUI 主题 | WebUI 主题 | `webui_theme` | `.setting-line` > `.settings-modal-icon-btn`（图标 `sun`/`moon`；提示 切换到浅色主题/切换到深色主题 `switch_to_light_theme`/`switch_to_dark_theme`） | 单击切换**整个 WebUI 页面**的明暗主题（emit `update:theme`，App.vue 改写 URL `?__theme=` 并重载）。**2026-10-16 由弹窗右上角迁入** |
| 自动填充·提示词 | 当网页加载后自动填充提示词 | `auto_input_prompt` | `.setting-line` + `.auto-input-row` | 下拉：禁止(`disabled`) / 最后输入的提示词(`last_input_prompt`) / 收藏里的条目 |
| 自动填充·反向词 | 同上（第二行） | `auto_input_prompt` | `.setting-line` + `.auto-input-row` | 同上 |
| 输入新关键词后自动翻译 | 输入新关键词后自动翻译 | `auto_translate` | `.settings-auto-translate-row` > `.gradio-checkbox`（图标 `translate`） | 开启后输入新词自动翻译。**语言"不可一键翻译"时拆成两个**：输入新关键词后自动翻译到本地语言(`auto_translate_to_local_language`，图标 `translate`) / …到英文(`auto_translate_to_english`，图标 `english`)。**非英文语言才显示** |

**② 翻译接口（`translate` → `translateSetting.vue`）**

| 控件 | 可见文案 | key | CSS 类名 | 行为 |
|---|---|---|---|---|
| 翻译接口下拉 | 翻译接口 | `translate_api` | `.setting-line` > `select` | 选翻译 API（选项名来自 `translate_apis.json`，会加 `[免费]/[申请后免费使用]` 前缀） |
| 无 Key 提示 | 免费的翻译接口不稳定，并不是每个接口都能在你的电脑中使用，请尽量申请api key使用稳定的官方接口 | `not_api_key_desc` | `.common-red` | 只读 |
| 帮助链接 | `[?] <链接>` | — | `.help-list` / `.help-item` | 外链 |
| API 配置项 | 各接口自己的配置项标题 | — | `.setting-line`（`input`/`select`） | 填 Key/地区等 |
| 翻译测试输入 | 翻译测试 | `translate_test` | `.test-input` | 测试文本 |
| 测试按钮 | 测试 | `test` | `.test-btn`（翻译中 `loading`） | 发起翻译测试 |
| 测试结果/错误 | — | — | `.translate-error` / `.test-input` | 显示结果 |
| 关键词组开关 | 使用关键词组增强翻译功能 | `enhance_translation_use_keyword_group` | `.onlyCsvOnAuto` | 用 `group_tags` 增强翻译 |
| TagComplete 说明 | 使用 … 扩展中的 danbooru.csv 增强翻译功能… | `tagcomplete_translate_desc` | `.setting-line` | 只读 |
| CSV 下拉 + 刷新 | 刷新 | `refresh` | `select` + `.refresh-btn`（图标 `refresh`/`loading`） | 选 CSV 词典 |
| 只用 CSV 开关 | 自动翻译只使用CSV翻译（不使用网络翻译），手动点击翻译按钮才使用CSV加网络翻译。 | `only_csv_on_auto` | `.onlyCsvOnAuto` | 自动翻译仅走词典 |
| TagComplete 测试 | 测试 | `test` | `.test-btn` | 测 翻译结果 |
| 保存 / 关闭 | 保存 / 关闭 | `save` / `close` | `.translate-save` / `.translate-close` | — |

**③ Prompt格式（`format` → `promptFormat.vue`）** — 一组复选框 `.format-item`（`.format-checkbox` + `.format-desc`）：

| 可见文案（key） | 说明 |
|---|---|
| 是否去除每个关键词逗号后的空格…（`is_remove_space`） | 去空格 |
| 是否去除Prompt最后的一个逗号…（`is_remove_last_comma`） | 去末逗号 |
| 是否保留关键词权重为0的格式…（`is_keep_weight_zero`） | 保留 `:0` |
| 是否保留关键词权重为1的格式…（`is_keep_weight_one`） | 保留 `:1`（当前模板未渲染） |
| 是否在 "BREAK" 关键词前面加换行符…（`is_break_before_wrap`） | BREAK 前换行 |
| 是否在 "BREAK" 关键词后面加换行符…（`is_break_after_wrap`） | BREAK 后换行 |
| 是否去除Lora前面的逗号…（`is_remove_lora_before_comma`） | Lora 前逗号 |
| 是否去除Lora后面的逗号…（`is_remove_lora_after_comma`） | Lora 后逗号 |
| 是否使用NovelAI的权重符号…（`is_use_novel_ai_weight_symbol`） | `()` → `{}` |
| 是否去除换行前面的逗号…（`is_remove_before_line_comma`） | 换行前逗号 |
| 是否在句号+空格处分割关键词…（`is_split_by_period`） | 按句号分词 |
| 是否同时分割括号前的句号+空格…（`is_split_by_period_include_paren`） | 上项子选项，勾选上项才出现 |

**④ 关键词黑名单（`blacklist` → `blacklist.vue`）**

| 控件 | 可见文案（key） | CSS 类名 |
|---|---|---|
| 说明 1 | 设置为黑名单的关键词，将被插件自动过滤！（`blacklist_desc`） | `.blacklist-desc` |
| 提示词黑名单 | 提示词 黑名单列表（`prompt_blacklist_list`） | `.blacklist-group` + `textarea.group-content`（占位：每行一个关键词 `one_keyword_per_line`） |
| 反向词黑名单 | 反向提示词 黑名单列表（`negative_prompt_blacklist_list`） | 同上 |
| Lora 黑名单 | Lora 黑名单列表（`lora_blacklist_list`） | 同上 |
| Lycoris 黑名单 | Lycoris 黑名单列表（`lycoris_blacklist_list`） | 同上 |
| Embedding 黑名单 | Embedding 黑名单列表（`embedding_blacklist_list`） | 同上 |
| 取消确认 | 从关键词列表扩展面板中加入黑名单时，取消《确认提示窗口》。（`cancel_confirm_add_blacklist`） | 复选框 |
| 说明 2 | 设为禁止翻译的词，插件将不会翻译它们！（`translate_blacklist_desc`） | `.blacklist-desc` |
| 禁译名单 | 禁止翻译的提示词列表（`disable_translate_prompt_blacklist_list`） | `textarea.group-content` |
| 保存 / 关闭 | 保存 / 关闭（`save` / `close`） | `.blacklist-save` / `.blacklist-close` |

**⑤ 快捷键设置（`hotkey` → `hotkey.vue`）** — 4 个下拉 `.hotkey-item`（`.hotkey-title` + `.hotkey-select`）：

| 行 | 可见文案（key） | 选项（key） |
|---|---|---|
| 1 | 左键点击关键词标签（`left_click_keyword_tag`） | 无(`none`) / 编辑关键词(`edit_keyword`) / 禁用/启用关键词(`disable_enable_keyword`) / 显示关键词扩展面板(`show_keyword_extend_panel`) |
| 2 | 右键点击关键词标签（`right_click_keyword_tag`） | 同上 |
| 3 | 双击点击关键词标签（`dblclick_keyword_tag`） | 同上 |
| 4 | 鼠标悬停关键词标签（`hover_keyword_tag`） | 无 / 显示关键词扩展面板 |
| 底部 | 保存 / 关闭（`save` / `close`） | `.hotkey-save` / `.hotkey-close` |

**⑥ 插件样式扩展（`theme` → `extensionCss.vue`）** — 表格 `.extension-table`，每行：复选框 `.extension-checkbox`、名称 `.extension-name`、类型 `.extension-type`、目录 `.extension-dir`、作者 `.extension-author`（`By: xxx`）。勾选即启用该样式扩展（数据源 `styles/extensions/*/manifest.json`）。

**⑦ 关于（`about` → `about.vue`）** — `.about-body`：标题 `globals.name`、版本 `版本: xxx`（`version`；无版本时显示 未知版本 `unknown_version`）、版本历史列表 `.version-list`（`.version-item` → `.version-sha` + `.version-date` + `.version-msg`）。**已切断联网，版本历史恒为空、版本显示"未知"，属预期。**

### 2.2 语言选择弹窗（`selectLanguage.vue`）

- **入口（2026-10-16 起）**：① 主入口 = 【设置弹窗 → 通用设置 → 界面语言】下拉（直接选，不经弹窗）；② 辅助入口 = packagesState 浮层的语言行（仍走本弹窗）。**顶栏原 `i18n` 图标已移除**。
- 结构：`.physton-prompt-select-language` → `.language-main` → `.language-list` → 每项 `.language-item`（文案 `code - 名称`，当前项带 `selected`）；右上 `close`。
- 行为：点某项即切换界面语言（写入 `languageCode`）。

### 2.3 历史记录浮层（`history.vue`）

- **入口**：主界面 `history` 图标；**鼠标离开或 3 秒未移入自动隐藏**。
- 顶部页签 `.popup-tabs` → `.popup-tab`（`tab-name` 文生图/图生图 + `tab-type` 提示词/反向词 + `tab-count` 条数）。
- 列表 `.content-list`：`删除所有历史记录` 按钮（`.clear-btn`，key `delete_all_history`；点后 confirm `delete_all_history_confirm`）；每条 `.content-item`：
  - 左：序号 `.item-header-index`、时间 `.item-header-time`、名称输入框 `.header-name-input`（占位 未设置名称 `unset_name`）
  - 右：`.header-btn-*` — 删除（`remove`）、收藏（`favorite-yes/no`）、复制（`copy`，`copy_to_clipboard`）、使用（`use`，`use`）
  - 提示文本 `.item-prompt`；**悬停条目**在侧边显示该条 `.popup-detail` 的标签明细
- 空态 `.content-empty`：暂无历史记录（`no_history`）/ 获取历史记录失败（`get_history_error`）

### 2.4 收藏列表浮层（`favorite.vue`）

- 结构与历史浮层基本一致（`.physton-prompt-favorite`），区别：**没有"删除全部"**，每条额外有 **上移 `.header-btn-move-up`（`move_up`）/ 下移 `.header-btn-move-down`（`move_down`）**；空态 暂无收藏（`no_favorite`）/ 获取收藏失败（`get_favorite_error`）。

### 2.5 ChatGPT 弹窗（`chatgptPrompt.vue`）

- **入口**：主界面 `chatgpt` 图标（仅正面框）。
- 三个可折叠面板 `.body-panel`（点 `.panel-unfold` 图标 `unfold` 折叠/展开）：
  1. **API配置**（`api_config`）— 配置项 `input/select` + **保存**按钮（`save`，`.common-btn`）
  2. **图片描述**（`image_desc`）— 「预设（`preset`）· 发给AI的第一句话（`ai_one`）」textarea + **恢复到系统默认**链接（`restore_to_default`）+「图片描述 · 发给AI的第二句话（`ai_two`）」textarea（占位 请输入图片描述，例如：一只猫坐在建筑物顶部，非常高清、非常真实的照片。`input_image_desc`）+ **生成**按钮（`generate`）
  3. **生成结果**（`generate_result`）— 结果 textarea + **使用**按钮（`use`）
- 右上 `close`；遮罩点击关闭。

### 2.6 额外网络信息浮层（`extraNetworksPopup.vue`）

- **触发**：悬停主界面里的额外网络卡片 / 带 `<lora:>` 的标签（由 `phystonPrompt` 发 `show-extra-networks`）。
- 结构 `.physton-prompt-extra-networks-popup` → `.popup-main`：预览图 `.info-preview` + `.info-raws` 字段行 `.info-raw`（`.raw-name` 名 + `.raw-value` 值，点值可复制）：
  - 模型名称 (name)（`model_name`）、输出名称 (output name)（`output_name`）、文件名 (filename)（`filename`）、文件路径（`filepath`）、触发关键词（`trained_words`，点单个词加入提示词，`.raw-words`）、描述（`description`）、Civitai 链接。
- 鼠标移出即隐藏。

### 2.7 依赖包状态弹窗（`packagesState.vue`）

- **触发**：启动时若有 Python 包未安装，自动弹出。
- 结构 `.physton-packages-state` → `.state-body`：`.today-now-show` 复选框「今日不再显示本窗口」（`today_not_show`）、名称、语言入口图标 `i18n`、说明 `.state-body-desc`（`packages_desc`）、包列表 `.package-list`（每项 `.package-name` / `.package-state` 已安装(`installed`)/未安装(`not_install`) / `.package-command` 命令）、**安装**按钮 `.btn-packages-install`（`install`）、安装输出 `.install-result`。

### 2.8 粘贴弹窗（`App.vue` 内联）

- **触发**：WebUI 原生粘贴按钮（🗒）被克隆出一个新按钮，点它打开。
- 结构 `.physton-paste-popup`：标题 `.paste-popup-title` + 内容 `textarea.paste-content`（占位 请输入内容 `please_enter_the_content_here`）+ **Submit** `.paste-submit`。把内容写进当前标签页的提示词框。

### 2.9 关键词高亮层（`highlightPrompt.vue`，无独立控件）

悬停某个标签时，在 WebUI 默认输入框位置**高亮**对应关键词（`.physton-highlight-prompt`），点击即隐藏。不是按钮，但若排查"输入框里文字变亮/被遮盖"类问题要想到它。

---

## 3. 常见"要改某个东西"的精确说法（示例）

| 你想表达的 | 建议说法 |
|---|---|
| 改设置弹窗左侧"通用设置"里的东西 | 设置弹窗 / 左侧标签栏 / 【通用设置】；再说具体控件文案 |
| 改那一排小图标 | 主界面 / 顶部图标栏 / 【设置】齿轮图标（`setting`） |
| 改某个标签的按钮 | 主界面 / 标签扩展面板（悬停标签出现）/ 【XXX】按钮 |
| 改分组标签面板底部 | 主界面 / 分组标签面板 / 底部工具栏 / 【刷新】或【宽度】 |
| 改某弹窗整体的外观 | 直接说弹窗名：设置弹窗 / 历史记录浮层 / 收藏列表浮层 / ChatGPT 弹窗 / 语言选择弹窗 / 依赖包弹窗 |

---

## 4. 已做过/需注意的 UI 约定

- 弹窗内图标统一 **16px**、跟随文字颜色；通用设置为"标题在上（小号灰字说明）、控件在下"的纵向紧凑版式（2026-10-16 UI1）。
- 每个弹窗的关闭方式：**设置弹窗**点右上 `close` 或点遮罩关闭；**语言/ChatGPT/黑名单/快捷键/样式扩展/关于**均为点遮罩或 `close` 关闭；**历史/收藏**为鼠标离开即隐藏。
- **设计令牌**（2026-10-16 P5a，规范移植自 `sd_forge_lora_new`）：根目录 `style.css` 末尾有「设计规范」块，定义 `--paio-*` 亮/暗双套令牌，并统一了**各弹窗**的：外壳底色/边框/圆角/投影、键盘焦点环（`:focus-visible` 2px 品牌色）、输入/下拉/复选框基线（高 28px、圆角 6px、字号 14px、复选框 14px + `accent-color`）、页脚按钮组（右对齐/gap 8px/上边框）、语义色。改弹窗配色**优先改令牌**，不要逐条写死颜色。品牌色为**紫蓝色**（`--paio-brand #6b73ff`），非橙色。
- 界面文案改动只需改 `i18n.json`（CRLF/indent=4），**刷新页面即生效**，不用重建前端。
- 改 `src/` 下模板/JS → **必须重建前端**；改根目录 `style.css` 无需重建。但**两者改完都别只按 F5**：Forge 在**启动时**把扩展 JS/CSS 的 `?mtime` 烘焙进页面 HTML，重建/改样式后**先点 设置页 → Actions → 「Reload custom script bodies (No ui updates, No restart)」，再刷新页面**，否则只能重启 WebUI 才看得到（详见 `项目开发说明.md` §5）。`i18n.json` 不受此限。
- 本插件的 DOM 容器清单（新增容器时需纳入 Forge 本地化屏蔽）见 `项目开发说明.md`。
