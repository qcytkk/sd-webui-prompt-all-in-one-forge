<template>
        <div :class="['physton-prompt-translate-setting', {'embedded-host': embedded}]" v-if="isOpen" @click="onCloseClick">
            <div class="translate-setting-main" @click.stop>
                <div class="translate-setting-close" v-if="!embedded" @click="onCloseClick">
                    <icon-svg name="close"/>
                </div>
                <div class="translate-setting-content" @click.stop>
                    <!-- ① 翻译流程：5 个翻译方案卡片，可拖动排序 + 单独开关。
                         数组顺序即尝试顺序：靠前的方案先翻译，未命中的词交给下一个方案 -->
                    <div class="settings-section">
                        <div class="setting-line paio-flow-head">
                            <!-- 第一行：标题在左、当前生效链徽标在右 -->
                            <div class="paio-flow-head-row">
                                <div class="line-title">{{ getLang('translation_source') }}</div>
                                <span class="paio-source-badge" :class="{'is-off': !flowList.some(i => i.enabled)}">
                                    {{ flowSummary() }}
                                </span>
                            </div>
                            <!-- 第二行：说明文字独占整行 -->
                            <div class="line-desc">{{ getLang('flow_order_hint') }}</div>
                        </div>
                        <div class="paio-flow-list" ref="flowList">
                            <div class="paio-flow-card" v-for="(item, index) in flowList" :key="item.key"
                                 :data-flow-key="item.key">
                                <span class="paio-flow-handle" aria-hidden="true" :title="getLang('flow_drag')">⋮⋮</span>
                                <span class="paio-flow-index" aria-hidden="true">{{ index + 1 }}</span>
                                <div class="paio-flow-text">
                                    <div class="paio-flow-title">{{ flowLabel(item.key) }}</div>
                                    <div class="paio-flow-desc">{{ flowDesc(item.key) }}</div>
                                </div>
                                <div class="paio-flow-actions">
                                    <button type="button" class="paio-icon-btn" :disabled="index === 0"
                                            :aria-label="getLang('flow_move_up')" :title="getLang('flow_move_up')"
                                            @click="moveFlow(index, -1)">↑</button>
                                    <button type="button" class="paio-icon-btn" :disabled="index === flowList.length - 1"
                                            :aria-label="getLang('flow_move_down')" :title="getLang('flow_move_down')"
                                            @click="moveFlow(index, 1)">↓</button>
                                    <div class="paio-pill" role="radiogroup" :aria-label="flowLabel(item.key)">
                                        <label class="paio-pill-btn">
                                            <input class="paio-pill-input" type="radio"
                                                   :name="'paio-flow-' + item.key" :checked="!item.enabled"
                                                   @change="toggleFlow(item.key, false)">
                                            <span>{{ getLang('toggle_off') }}</span>
                                        </label>
                                        <label class="paio-pill-btn">
                                            <input class="paio-pill-input" type="radio"
                                                   :name="'paio-flow-' + item.key" :checked="item.enabled"
                                                   @change="toggleFlow(item.key, true)">
                                            <span>{{ getLang('toggle_on') }}</span>
                                        </label>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <!-- 关键词组说明（开关已并入上方卡片，这里只保留解释） -->
                        <div class="setting-line paio-col">
                            <div class="line-text">
                                <div class="line-title">{{ getLang('Keyword_group') }}</div>
                            </div>
                            <div class="line-content">
                                <div v-html="getLang('enhance_translation_use_Keyword_group_desc')"></div>
                            </div>
                        </div>
                        <!-- 内容较多，右列纵向分 4 行：说明 / 红字警告 / 控件行(下拉+刷新+勾选框) / 勾选框说明 -->
                        <div class="setting-line paio-col">
                            <div class="line-text">
                                <!-- 标题分两行：产品名一行、中文注解一行（沿用 title + desc 的左列两行写法） -->
                                <div class="line-title">TagComplete</div>
                                <div class="line-desc">{{ getLang('tag_complete_dict') }}</div>
                            </div>
                            <div class="line-content">
                                <div v-html="getLang('tagcomplete_translate_desc')"></div>
                                <div class="common-red" v-html="getLang('tagcomplete_translate_desc2')"></div>
                                <div class="line-row">
                                    <select v-model="tagCompleteFileKey" @change="onTagCompleteFileChange($event)">
                                        <option v-for="item in tagCompleteFiles" :value="item.key">{{ item.name }}</option>
                                    </select>
                                    <div class="refresh-btn hover-scale-120" v-tooltip="getLang('refresh')" @click="refreshCSVs">
                                        <icon-svg v-if="tagCompleteFilesLoading" name="loading"/>
                                        <icon-svg v-else name="refresh" />
                                    </div>
                                </div>
                                <!-- 勾选框与它的说明文字成对放在同一行 -->
                                <label class="onlyCsvOnAuto" v-show="tagCompleteFileKey">
                                    <input class="hover-scale-120" type="checkbox" value="1"
                                           v-model="onlyCsvOnAutoValue" @change="onOnlyCsvOnAutoChange($event)">
                                    <span>{{ getLang('only_csv_on_auto') }}</span>
                                </label>
                            </div>
                        </div>
                        <!-- 本行属于上方 TagComplete 功能，标 .paio-sub：与上一行之间不再画虚线 -->
                        <div class="setting-line paio-sub" v-show="tagCompleteFileKey">
                            <div class="line-text"></div>
                            <div class="line-content">
                                <div class="hover-scale-120 test-btn" @click="onTagCompleteTestClick">{{ getLang('test') }}</div>
                                <div ref="tagCompleteResults" v-show="tagCompleteResults.length > 0">
                                    <p v-for="text in tagCompleteResults" :key="text">{{ text }}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    <!-- ② 机翻词典：缓存【连网翻译】与【本地AI大模型翻译】的成功译文，
                         命中后不再重复消耗网络/显存。文件为 storage/machine_dict.csv。
                         与上一组 TagComplete 之间保留虚线分隔（.settings-section+.settings-section） -->
                    <div class="settings-section paio-plain">
                        <div class="setting-line paio-side">
                            <div class="line-text">
                                <div class="line-title">{{ getLang('machine_dict') }}</div>
                                <div class="line-desc">{{ getLang('machine_dict_sub') }}</div>
                            </div>
                            <div class="line-content">
                                <div class="paio-side-block">
                                    <div v-html="getLang('machine_dict_desc')"></div>
                                    <div class="line-row">
                                        <span class="paio-source-badge" :class="{'is-off': !machineDict.count}">
                                            {{ machineDictText }}
                                        </span>
                                        <button type="button" class="paio-btn" :aria-busy="machineDictLoading ? 'true' : 'false'"
                                                @click="refreshMachineDict">
                                            <icon-svg name="refresh" :class="{'is-spinning': machineDictLoading}"/>
                                            <span>{{ getLang('refresh') }}</span>
                                        </button>
                                        <button type="button" class="paio-btn" :disabled="!machineDict.count"
                                                @click="exportMachineDict">
                                            <icon-svg name="unfold"/>
                                            <span>{{ getLang('machine_dict_export') }}</span>
                                        </button>
                                        <button type="button" class="paio-btn" :disabled="machineDictClearing || !machineDict.count"
                                                @click="clearMachineDict">
                                            <icon-svg v-if="machineDictClearing" name="loading" class="is-spinning"/>
                                            <span>{{ getLang('machine_dict_clear') }}</span>
                                        </button>
                                    </div>
                                    <div class="line-desc">{{ getLang('machine_dict_file_hint') }}{{ machineDict.file }}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <!-- ③ 连网翻译接口：标题在左列、内容在右列（与连网翻译测试同款两栏布局）；
                         右列把「接口下拉 + 免费提示/帮助链接 + 各接口参数」套成一个块。
                         与上一组的 TagComplete 之间**保留虚线分隔**（来自 .settings-section+.settings-section） -->
                    <div class="settings-section paio-plain">
                        <div class="setting-line paio-side">
                            <div class="line-text">
                                <div class="line-title">{{ getLang('translate_api') }}</div>
                            </div>
                            <div class="line-content">
                                <div class="paio-side-block">
                                    <!-- 翻译接口下拉：占满整行宽度、左对齐 -->
                                    <div class="paio-param-row paio-fill">
                                        <div class="line-text"></div>
                                        <div class="paio-param-ctl">
                                            <select :aria-label="getLang('translate_api')" v-model="apiKey" @change="onApiKeyChange($event)">
                                                <optgroup v-for="typeGroup in supportApi" :key="typeGroup.type"
                                                          :label="getLang(typeGroup.type)">
                                                    <option v-for="item in typeGroup.children" :key="item.key" :value="item.key" :disabled="item.disabled">
                                                        {{ getItemName(item) }}
                                                    </option>
                                                </optgroup>
                                            </select>
                                        </div>
                                    </div>
                                    <!-- 免费接口提示（仅 translators 类接口）与帮助链接同一行、左右两栏 -->
                                    <div class="paio-split" v-if="apiItem && (apiItem.type == 'translators' || apiItem.help)">
                                        <span class="common-red" v-if="apiItem.type == 'translators'">*{{ getLang('not_api_key_desc') }}</span>
                                        <div class="help-list" v-if="apiItem.help">
                                            <div v-for="item in apiItem.help" class="help-item">[?] <a :href="item.url" target="_blank">{{ item.title }}</a></div>
                                        </div>
                                    </div>
                                    <!-- 各接口参数：名称在左、控件在右 -->
                                    <div class="paio-param-row" v-for="config in configs">
                                        <div class="line-text">
                                            <div class="line-title">{{ configLabel(config) }}</div>
                                        </div>
                                        <div class="paio-param-ctl">
                                            <input type="text" v-if="config.type == 'input'" v-model="config.value" @change="onChangeConfigValue(config)">
                                            <select v-if="config.type == 'select'" v-model="config.value" @change="onConfigSelectChange(config, $event)">
                                                <option v-for="option in config.options" :value="option">{{ option }}</option>
                                            </select>
                                            <div v-if="config.desc" v-html="config.desc"></div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <!-- ④ 连网翻译测试：与上一组「连网翻译接口」视作同一个整体
                         （.paio-no-sep 去掉组间虚线与额外间距）；右列把「两栏 textarea + 测试按钮」套成一个块 -->
                    <div class="settings-section paio-plain paio-no-sep">
                        <div class="setting-line paio-side">
                            <div class="line-text">
                                <div class="line-title">{{ getLang('translate_test') }}</div>
                            </div>
                            <div class="line-content">
                                <div class="paio-side-block">
                                    <!-- 第一行两栏：左=翻译原文，右=翻译结果 -->
                                    <div class="paio-test-pair">
                                        <textarea class="test-input" :aria-label="getLang('translate_test')" v-model="testText"></textarea>
                                        <textarea class="test-input" :aria-label="getLang('translate_result')" v-model="translatedText"></textarea>
                                    </div>
                                    <!-- 第二行：测试按钮（失败时在其左侧显示错误信息） -->
                                    <div class="paio-test-actions">
                                        <div class="translate-error" v-if="!translateSuccess && errorMessage">{{ errorMessage }}</div>
                                        <div class="hover-scale-120 test-btn" @click="onTestClick">
                                            <icon-svg v-if="loading" name="loading"/>
                                            <template v-else>{{getLang('test')}}</template>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <!-- ⑤ 本地AI大模型翻译：与 sd_forge_lora_new 共用 lna_llm_service（同一模型实例 / 同一把推理锁 /
                         同一套空闲卸载逻辑）。默认由 .settings-section+.settings-section 画虚线，与上一组隔开 -->
                    <div class="settings-section paio-plain">
                        <!-- 本区块统一采用 .paio-stack 纵向三段式：标签 / 小字注解 / 控件（2026-10-18 @TraeCode） -->
                        <!-- div 1：运行环境（llama.cpp 构建 / CUDA 运行库）—— 放在最前，先确认环境再选模型 -->
                        <div class="setting-line paio-stack">
                            <div class="line-text">
                                <div class="line-title">{{ getLang('llm_runtime') }}</div>
                                <div class="line-desc">
                                    {{ getLang('llm_runtime_desc') }}
                                    <a class="paio-link" href="https://github.com/qcytkk/sd_forge_lora_new"
                                       target="_blank" rel="noopener noreferrer">https://github.com/qcytkk/sd_forge_lora_new</a>
                                </div>
                            </div>
                            <div class="line-content">
                                <div class="line-row">
                                    <span class="paio-source-badge" :class="{'is-off': !llm.engine_ready}">{{ llmRuntimeText }}</span>
                                    <div class="hover-scale-120 test-btn" v-if="llm.showCudaDownload" @click="onLLMDownloadCuda">
                                        <icon-svg v-if="llmCudaDownloading" name="loading"/>
                                        <template v-else>{{ getLang('llm_runtime_download_cuda') }}</template>
                                    </div>
                                </div>
                                <div class="common-red" v-if="llm.error">{{ llm.error }}</div>
                            </div>
                        </div>
                        <!-- div 2：标题 + 说明 + 模型选择 + 刷新 / 打开目录 -->
                        <div class="setting-line paio-stack">
                            <div class="line-text">
                                <div class="line-title">{{ getLang('llm_local_title') }}</div>
                                <div class="line-desc">{{ getLang('llm_local_desc') }}</div>
                            </div>
                            <div class="line-content">
                                <div class="line-row">
                                    <select :aria-label="getLang('llm_model')" v-model="llmSelected"
                                            :disabled="llmSwitching || !llm.available" @change="onLLMModelChange($event)">
                                        <option value="">{{ getLang('llm_model_none') }}</option>
                                        <option v-for="item in llmModels" :key="item.rel" :value="item.rel">{{ item.rel }}</option>
                                    </select>
                                    <button type="button" class="paio-btn" :aria-busy="llmLoading ? 'true' : 'false'"
                                            @click="refreshLLM">
                                        <icon-svg name="refresh" :class="{'is-spinning': llmLoading}"/>
                                        <span>{{ getLang('llm_refresh') }}</span>
                                    </button>
                                    <button type="button" class="paio-btn" @click="openLLMFolder">
                                        <icon-svg name="unfold"/>
                                        <span>{{ getLang('llm_open_folder') }}</span>
                                    </button>
                                </div>
                            </div>
                        </div>
                        <!-- div 2：推理设备（CPU / GPU）——两栏布局：左=标题+注解，右=控件 -->
                        <div class="setting-line paio-two-col">
                            <div class="line-text">
                                <div class="line-title">{{ getLang('llm_device') }}</div>
                                <div class="line-desc">{{ getLang('llm_device_desc') }}</div>
                                <div class="line-desc" v-if="!llm.cuda_available">{{ getLang('llm_gpu_unavailable') }}</div>
                            </div>
                            <div class="line-content">
                                <div class="paio-pill" role="radiogroup" :aria-label="getLang('llm_device')">
                                    <label class="paio-pill-btn">
                                        <input class="paio-pill-input" type="radio" name="paio-llm-device"
                                               :checked="!llm.gpu" :disabled="llmSwitching || !llm.available"
                                               @change="onLLMGpuChange(false)">
                                        <span>{{ getLang('llm_cpu') }}</span>
                                    </label>
                                    <label class="paio-pill-btn">
                                        <input class="paio-pill-input" type="radio" name="paio-llm-device"
                                               :checked="llm.gpu" :disabled="llmSwitching || !llm.available || !llm.cuda_available"
                                               @change="onLLMGpuChange(true)">
                                        <span>{{ getLang('llm_gpu') }}</span>
                                    </label>
                                </div>
                            </div>
                        </div>
                        <!-- div 3：空闲自动卸载 + 空闲分钟数 + 模型状态按钮 + 加载状态文字
                             （lora_new 启用时空闲设置冻结，仅显示） -->
                        <div class="setting-line paio-stack">
                            <div class="line-text">
                                <div class="line-title">{{ getLang('llm_idle_auto') }}</div>
                                <div class="line-desc" v-if="llm.frozen">{{ getLang('llm_frozen_by_lora') }}</div>
                            </div>
                            <div class="line-content">
                                <div class="line-row">
                                    <label class="onlyCsvOnAuto">
                                        <input class="hover-scale-120" type="checkbox" :checked="llm.auto_unload"
                                               :disabled="llm.frozen" @change="onLLMIdleToggle($event)">
                                        <span>{{ getLang('llm_idle_minutes') }}</span>
                                    </label>
                                    <input class="paio-num-input" type="number" min="3" max="200" step="1"
                                           v-model.number="llmIdleMinutes" :disabled="llm.frozen || !llm.auto_unload"
                                           @change="onLLMIdleMinutesChange">
                                    <!-- 与 sd_forge_lora_new 顶栏同款的「翻译模型状态」按钮：
                                         未加载=灰色只读；已加载=绿色，悬停转红并提示「卸载翻译模型」。
                                         模型实例两边共享，所以手动卸载不受 frozen 限制 -->
                                    <button type="button" class="paio-llm-state" :class="{'is-loaded': llm.loaded}"
                                            :disabled="!llm.loaded || llmUnloading"
                                            :aria-label="llm.loaded ? getLang('llm_state_aria_loaded') : getLang('llm_state_aria_off')"
                                            @click="onLLMUnload">
                                        <span class="paio-llm-state-dot" aria-hidden="true"></span>
                                        <span class="paio-llm-state-text paio-llm-state-off">{{ getLang('llm_state_off') }}</span>
                                        <span class="paio-llm-state-text paio-llm-state-on">{{ getLang('llm_state_on') }}</span>
                                        <span class="paio-llm-state-text paio-llm-state-hover">{{ getLang('llm_state_hover') }}</span>
                                    </button>
                                </div>
                                <!-- 第四行：模型加载状态文字（未加载灰、已加载绿） -->
                                <div class="line-row">
                                    <div class="paio-status-text" :class="llm.loaded ? 'is-on' : 'is-off'">{{ llmStatusText }}</div>
                                    <div class="line-desc" v-if="llmBusy">{{ getLang('llm_busy') }}</div>
                                </div>
                            </div>
                        </div>
                        <!-- div 6：本地翻译测试（与连网翻译测试同款两栏 + 测试按钮） -->
                        <div class="setting-line paio-stack">
                            <div class="line-text">
                                <div class="line-title">{{ getLang('llm_local_test') }}</div>
                            </div>
                            <div class="line-content">
                                <div class="paio-side-block">
                                    <div class="paio-test-pair">
                                        <textarea class="test-input" :aria-label="getLang('llm_local_test')" v-model="llmTestText"></textarea>
                                        <textarea class="test-input" :aria-label="getLang('translate_result')" v-model="llmTranslatedText"></textarea>
                                    </div>
                                    <div class="paio-test-actions">
                                        <div class="translate-error" v-if="llmTestError">{{ llmTestError }}</div>
                                        <div class="hover-scale-120 test-btn" @click="onLLMTestClick">
                                            <icon-svg v-if="llmTesting" name="loading"/>
                                            <template v-else>{{ getLang('test') }}</template>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <!-- div 7：AI翻译提示词（模型需要明确的目标语言与输出格式约束） -->
                        <div class="setting-line paio-stack">
                            <div class="line-text">
                                <div class="line-title">{{ getLang('llm_prompt_title') }}</div>
                                <div class="line-desc">{{ getLang('llm_prompt_desc') }}</div>
                            </div>
                            <div class="line-content">
                                <div class="paio-side-block">
                                    <textarea class="test-input paio-prompt-input" :aria-label="getLang('llm_prompt_title')"
                                              :placeholder="getLang('llm_prompt_placeholder')" v-model="llmAiPrompt"></textarea>
                                    <div class="paio-test-actions">
                                        <div class="translate-error" v-if="llmPromptMsg">{{ llmPromptMsg }}</div>
                                        <button type="button" class="paio-btn" @click="onLLMPromptReset">
                                            <span>{{ getLang('llm_prompt_reset') }}</span>
                                        </button>
                                        <button type="button" class="paio-btn" :disabled="llmPromptSaving"
                                                :aria-busy="llmPromptSaving ? 'true' : 'false'"
                                                @click="onLLMPromptSave">
                                            <icon-svg v-if="llmPromptSaving" name="loading" class="is-spinning"/>
                                            <span>{{ getLang('llm_prompt_save') }}</span>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <!-- div 8：运行状态提示（未启用插件 / 未选模型 / 加载失败） -->
                        <div class="setting-line" v-if="llmHint">
                            <div class="line-text">
                                <div class="line-desc">{{ llmHint }}</div>
                            </div>
                            <div class="line-content"></div>
                        </div>
                        <!-- div 9：引擎缺失提示 -->
                        <div class="setting-line" v-if="llm.notInstalled">
                            <div class="line-text">
                                <div class="line-desc common-red">{{ getLang('llm_engine_missing') }}</div>
                            </div>
                            <div class="line-content"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
</template>
<script>
import LanguageMixin from "@/mixins/languageMixin";
import common from "@/utils/common";
import IconSvg from "@/components/iconSvg.vue";
import Sortable from "sortablejs";

// 翻译流程支持的五个方案（初始顺序；实际顺序由用户在设置里拖动决定）
const FLOW_KEYS = ['group_tags', 'tag_dict', 'machine_dict', 'network', 'local_llm'];
const DEFAULT_FLOW = [
    {key: 'group_tags', enabled: true},
    {key: 'tag_dict', enabled: true},
    {key: 'machine_dict', enabled: true},
    {key: 'network', enabled: true},
    {key: 'local_llm', enabled: false},
];

export default {
    name: 'TranslateSetting',
    components: {IconSvg},
    mixins: [LanguageMixin],
    props: {
        embedded: {type: Boolean, default: false},
    },
    data() {
        return {
            testText: '',
            translateSuccess: false,
            errorMessage: '',
            translatedText: '',
            loading: false,
            isOpen: false,
            configs: [],
            apiKey: '',
            tagCompleteFiles: [],
            tagCompleteFilesLoading: false,
            tagCompleteFileKey: '',
            tagCompleteResults: [],
            onlyCsvOnAutoValue: false,

            groupTagsTranslateValue: true,

            // 机翻词典：缓存连网 / 本地大模型翻译的对照（storage/machine_dict.csv）
            machineDict: {count: 0, size: 0, file: 'machine_dict.csv'},
            machineDictLoading: false,
            machineDictClearing: false,

            // 翻译流程：五张卡片的拖动排序实例（列表数据见 computed.flowList）
            flowSortable: null,

            // ── 本地AI大模型翻译（与 sd_forge_lora_new 共用 lna_llm_service）──
            llmModels: [],
            llmSelected: '',
            llmLoading: false,
            llmSwitching: false,
            llmIdleMinutes: 5,
            llmBusy: false,
            llm: {
                available: false,   // 共享服务可用（sd_forge_lora_new 存在且可导入）
                notInstalled: false,// 共享服务目录不存在
                frozen: false,      // lora_new 启用 → 卸载相关设置冻结
                gpu: false,
                cuda_available: false,
                engine_ready: false,
                loaded: false,
                model: '',
                auto_unload: true,
                idle_minutes: 5,
                error: '',
                note: '',
                runtime: null,
                cudaDownloading: false,
            },
            llmTestText: '',
            llmTranslatedText: '',
            llmTestError: '',
            llmTesting: false,
            llmUnloading: false,
            // AI翻译提示词（自定义模板，保存在 storage/local_llm_prompt.json）
            llmAiPrompt: '',
            llmAiPromptDefault: '',
            llmPromptSaving: false,
            llmPromptMsg: '',
            llmTimer: null,
        }
    },
    computed: {
        apiItem() {
            return common.getTranslateApiItem(this.translateApis, this.apiKey)
        },
        supportApi() {
            if (!this.translateApis || this.translateApis.length <= 0) return []
            let api = JSON.parse(JSON.stringify(this.translateApis))
            api.forEach(group => {
                // 本地大模型已有独立的【翻译流程】卡片与设置区，
                // 不再出现在「连网翻译接口」下拉里（后端仍保留该条目供 BaseTranslator 查语言表）
                group.children = group.children.filter(item => item.key !== 'local_llm')
                group.children.forEach(item => {
                    item.disabled = !item.support[this.languageCode]
                })
            })
            return api.filter(group => group.children.length > 0)
        },
        // 翻译流程的五张卡片：以父组件传入的 translateFlow 为准，
        // 本地维护一份副本，拖动/开关后 emit 回去
        flowList: {
            get() {
                const src = Array.isArray(this.translateFlow) && this.translateFlow.length
                    ? this.translateFlow : DEFAULT_FLOW
                const list = src.filter(item => item && FLOW_KEYS.includes(item.key))
                // 补齐缺失的方案（老数据升级）：按 FLOW_KEYS 的顺序插回原位置，
                // 开关状态取默认值（新方案【机翻词典】默认参与翻译流程）
                FLOW_KEYS.forEach((key, defaultIndex) => {
                    if (list.some(item => item.key === key)) return
                    const def = DEFAULT_FLOW.find(item => item.key === key) || {key, enabled: false}
                    let insertAt = list.length
                    for (let i = 0; i < list.length; i++) {
                        if (FLOW_KEYS.indexOf(list[i].key) > defaultIndex) {
                            insertAt = i
                            break
                        }
                    }
                    list.splice(insertAt, 0, {key, enabled: !!def.enabled})
                })
                return list
            },
            set(val) {
                this.$emit('update:translateFlow', val.map(item => ({key: item.key, enabled: !!item.enabled})))
            }
        },
        // 机翻词典：条数 / 体积徽标
        machineDictText() {
            const count = this.machineDict.count || 0
            if (!count) return this.getLang('machine_dict_empty')
            return this.getLang('machine_dict_count').replace('{0}', String(count)).replace('{1}', this.formatSize(this.machineDict.size))
        },
        // 共享服务不可用时的提示：区分「插件目录缺失」与「模块导入失败」
        llmPromptText() {
            if (this.llm.notInstalled) return this.getLang('llm_not_enabled_plugin')
            return this.getLang('llm_service_error') + (this.llm.error ? ' ' + this.llm.error : '')
        },
        // 本地大模型：运行环境说明（CUDA / CPU / 缺失）
        llmRuntimeText() {
            if (!this.llm.available) return this.llmPromptText
            const rt = this.llm.runtime
            if (!rt || !rt.installed) return this.getLang('llm_engine_missing')
            if (rt.build === 'cuda') return this.getLang('llm_runtime_cuda_ok')
            return this.getLang('llm_runtime_cpu')
        },
        // 模型加载状态：已加载 / 未加载 / 切换中
        llmStatusText() {
            if (this.llmSwitching) return this.getLang('llm_switching')
            if (this.llm.loaded) return this.getLang('llm_state_on')
            return this.getLang('llm_state_off')
        },
        // 状态提示：未启用共享服务 / 未选模型 / 加载失败 / 翻译中的原因
        llmHint() {
            if (!this.llm.available) return this.llmPromptText
            if (!this.llm.error && this.llm.note) return this.llm.note
            if (!this.llm.error && !this.llmSelected) return this.getLang('llm_no_model')
            return ''
        },
    },
    mounted() {
        this.translateSuccess = false
        this.errorMessage = ''
        this.translatedText = ''
        this.loading = false
    },
    beforeUnmount() {
        this.stopLLMPolling()
        if (this.flowSortable) {
            this.flowSortable.destroy()
            this.flowSortable = null
        }
    },
    emits: ['update:translateApi', 'forceUpdate:translateApi', 'update:tagCompleteFile', 'update:onlyCsvOnAuto', 'update:groupTagsTranslate', 'update:translateFlow'],
    watch: {
        apiKey: {
            handler: function (val, oldVal) {
                this.translateSuccess = false
                this.errorMessage = ''
                this.translatedText = ''
                this.loading = false
                this.configs = []
                this.gradioAPI.getData('translate_api.' + this.apiKey).then(res => {
                    const apiItem = this.apiItem
                    if (apiItem && apiItem.config) {
                        for (const item of this.apiItem.config) {
                            if (res) {
                                item.value = res[item.key] || item.default
                            } else {
                                item.value = item.default || ''
                            }
                            this.configs.push(item)
                        }
                        console.log(this.configs)
                    }
                })
            },
            immediate: false
        },
        /*configs: {
            handler: function (val, oldVal) {
                val.forEach(config => {
                    if (config.value === '') {
                        config.value = config.default
                    }
                })
            },
            deep: true
        },*/
    },
    methods: {
        open(apiKey) {
            this.testText = 'Hi, this is a test message for the translation API.'
            this.testText = common.replaceGlobals(this.testText)
            this.apiKey = apiKey
            this.isOpen = true
            this.errorMessage = ''
            this.translatedText = ''
            this.loading = false
            this.tagCompleteFileKey = this.tagCompleteFile
            this.onlyCsvOnAutoValue = this.onlyCsvOnAuto
            this.groupTagsTranslateValue = this.groupTagsTranslate
            this.refreshCSVs()
            this.refreshMachineDict()
            this.llmTestText = 'Hi, this is a test message for the translation API.'
            this.llmTestText = common.replaceGlobals(this.llmTestText)
            this.llmTranslatedText = ''
            this.llmTestError = ''
            this.llmTesting = false
            this.refreshLLM()
            this.loadLLMPrompt()
            this.startLLMPolling()
            this.$nextTick(() => this.initFlowSortable())
        },
        getItemName(item) {
            let name = item.name
            name = name.replace('[Free] ', '[' + this.getLang('free') + '] ')
            name = name.replace('[ApiKey] ', '[' + this.getLang('apply_for_free') + '] ')
            // 不足100个字符的，用空格补齐
            /*if (name.length < 30) {
                name += new Array(30 - name.length).join('　')
            }
            name += '[QPS: ' + (item.concurrent || 1) + ']'*/
            return name
        },
        // 接口参数名默认沿用 translate_apis.json 的英文 title（技术名词，保持英文）；
        // 只有「语言/市场型」的 region（选项为 CN/EN/JP 这类两字母代码，即 translators 类接口）
        // 额外补一个中文注解，避免与机房地域（cn-shanghai 等）混淆。
        configLabel(config) {
            if (config.key === 'region' && config.type === 'select'
                && Array.isArray(config.options) && config.options.length > 0
                && config.options.every(option => /^[A-Z]{2}$/.test(option))) {
                return this.getLang('api_region_market')
            }
            return config.title
        },
        formatSize(size) {
            size = Number(size) || 0
            if (size < 1024) return size + ' B'
            if (size < 1024 * 1024) return (size / 1024).toFixed(1) + ' KB'
            return (size / 1024 / 1024).toFixed(1) + ' MB'
        },
        refreshMachineDict() {
            if (this.machineDictLoading) return
            this.machineDictLoading = true
            return this.gradioAPI.machineDictStats().then(res => {
                this.machineDictLoading = false
                if (!res) return
                this.machineDict = {
                    count: res.count || 0,
                    size: res.size || 0,
                    file: res.file || 'machine_dict.csv',
                }
            }).catch(() => {
                this.machineDictLoading = false
            })
        },
        // 导出机翻词典 CSV（直接用浏览器下载，可自行编辑后再放回 storage/）
        exportMachineDict() {
            const url = common.apiUrl() + 'machine_dict/file?t=' + new Date().getTime()
            const link = document.createElement('a')
            link.href = url
            link.download = this.machineDict.file || 'machine_dict.csv'
            document.body.appendChild(link)
            link.click()
            link.remove()
        },
        clearMachineDict() {
            if (this.machineDictClearing || !this.machineDict.count) return
            if (!window.confirm(this.getLang('machine_dict_clear_confirm'))) return
            this.machineDictClearing = true
            this.gradioAPI.machineDictClear().then(() => {
                this.machineDictClearing = false
                this.refreshMachineDict()
                this.$toastr.success(this.getLang('success'))
            }).catch(() => {
                this.machineDictClearing = false
                this.$toastr.error(this.getLang('failed'))
            })
        },
        refreshCSVs() {
            if (this.tagCompleteFilesLoading) return
            this.tagCompleteFilesLoading = true
            this.tagCompleteFiles = []
            return this.gradioAPI.getCSVs().then(res => {
                this.tagCompleteFilesLoading = false
                if (!res || res.length <= 0) return
                this.tagCompleteFiles.push({
                    key: '',
                    name: this.getLang('not_enable'),
                })
                for (const item of res) {
                    this.tagCompleteFiles.push({
                        key: item.key,
                        name: item.key,
                    })
                }
            }).catch(err => {
                this.tagCompleteFilesLoading = false
            })
        },
        onTestClick() {
            if (this.loading) return
            this.translateSuccess = false
            this.errorMessage = ''
            this.translatedText = ''
            this.loading = true
            let configs = {}
            for (const item of this.configs) {
                configs[item.key] = item.value
            }
            this.translate(this.testText, 'en_US', this.languageCode, this.apiKey, configs).then(res => {
                if (!res.success) {
                    this.errorMessage = res.message
                } else {
                    this.translatedText = res.translated_text
                    this.translateSuccess = true
                }
                this.loading = false
            }).catch(err => {
                this.errorMessage = err.message
                this.loading = false
            })
        },
        translate(text, from_lang, to_lang, translateApi = null, translateApiConfig = null) {
            return new Promise(async (resolve, reject) => {
                translateApi = translateApi || this.translateApi
                translateApiConfig = translateApiConfig || this.translateApiConfig || {}

                this.gradioAPI.translate(text, from_lang, to_lang, translateApi, translateApiConfig).then(res => {
                    if (res.success) {
                        resolve(res)
                    } else {
                        reject(res)
                    }
                }).catch(error => {
                    reject(error)
                })
            })
        },
        // ── 改动即保存（替代原来的「保存」按钮）──
        // translateApi / tagCompleteFile / onlyCsvOnAuto / groupTagsTranslate 在 App.vue 里各自有 watcher，
        // emit 上去就会落盘；只有「当前 API 的参数对象」不在 watcher 覆盖范围内，需要显式 setData。
        saveConfigs() {
            let configs = {}
            for (const item of this.configs) {
                configs[item.key] = item.value
            }
            this.gradioAPI.setData('translate_api.' + this.apiKey, configs).then(res => {
                if (this.apiKey === this.translateApi) this.$emit('forceUpdate:translateApi')
            })
        },
        onApiKeyChange(e) {
            // 注意：此刻 this.configs 还属于「上一个 API」，不能在这里保存参数；
            // 参数是在各自字段 change 时、按当时的 apiKey 保存的
            this.$emit('update:translateApi', e.target.value)
        },
        onChangeConfigValue(config) {
            if (config.type === 'input' && config.value === '' && config.default) {
                config.value = config.default
            }
            this.saveConfigs()
        },
        onConfigSelectChange(config, e) {
            config.value = e.target.value
            this.saveConfigs()
        },
        onTagCompleteFileChange(e) {
            this.tagCompleteResults = []
            this.tagCompleteFileKey = e.target.value
            this.$emit('update:tagCompleteFile', e.target.value)
        },
        onOnlyCsvOnAutoChange(e) {
            this.onlyCsvOnAutoValue = e.target.checked
            this.$emit('update:onlyCsvOnAuto', e.target.checked)
        },
        onGroupTagsTranslateChange(e) {
            this.groupTagsTranslateValue = e.target.checked
            this.$emit('update:groupTagsTranslate', e.target.checked)
        },
        // ── 翻译流程：卡片名称 / 说明 / 排序 / 开关 ──
        flowLabel(key) {
            return {
                group_tags: this.getLang('flow_name_group_tags'),
                tag_dict: this.getLang('flow_name_tag_dict'),
                machine_dict: this.getLang('flow_name_machine_dict'),
                network: this.getLang('flow_name_network'),
                local_llm: this.getLang('flow_name_local_llm'),
            }[key] || key
        },
        flowDesc(key) {
            return {
                group_tags: this.getLang('flow_desc_group_tags'),
                tag_dict: this.getLang('flow_desc_tag_dict'),
                machine_dict: this.getLang('flow_desc_machine_dict'),
                network: this.getLang('flow_desc_network'),
                local_llm: this.getLang('flow_desc_local_llm'),
            }[key] || ''
        },
        // 左列「翻译流程」总览：只列出已启用的方案，顺序与卡片一致
        flowSummary() {
            const enabled = this.flowList.filter(item => item.enabled).map(item => this.flowLabel(item.key))
            return enabled.length ? enabled.join(' → ') : this.getLang('flow_none')
        },
        moveFlow(index, delta) {
            const list = this.flowList.slice()
            const target = index + delta
            if (target < 0 || target >= list.length) return
            const [item] = list.splice(index, 1)
            list.splice(target, 0, item)
            this.flowList = list
        },
        toggleFlow(key, enabled) {
            this.flowList = this.flowList.map(item => (
                item.key === key ? {key: item.key, enabled} : {key: item.key, enabled: item.enabled}
            ))
        },
        initFlowSortable() {
            if (this.flowSortable || !this.$refs.flowList) return
            this.flowSortable = Sortable.create(this.$refs.flowList, {
                animation: 150,
                handle: '.paio-flow-handle',
                draggable: '.paio-flow-card',
                onEnd: () => {
                    // 以拖动后的 DOM 顺序为准，回写 flowList
                    const keys = Array.from(this.$refs.flowList.children)
                        .map(el => el.getAttribute('data-flow-key'))
                        .filter(key => key)
                    const map = {}
                    this.flowList.forEach(item => { map[item.key] = item.enabled })
                    this.flowList = keys.filter(key => key in map)
                        .map(key => ({key, enabled: !!map[key]}))
                },
            })
        },
        onCloseClick() {
            this.isOpen = false
            this.stopLLMPolling()
        },
        onTagCompleteTestClick() {
            this.tagCompleteResults = []
            const texts = ['1girl', 'Robot dog']
            texts.forEach(text => {
                let lang = this.getLang('translate_result')
                this.translateToLocalByCSV(text, this.tagCompleteFileKey, true).then(res => {
                    this.tagCompleteResults.push(lang.replace('{0}', text).replace('{1}', res))
                    /*this.$refs.tagCompleteResults.scrollIntoView({
                        behavior: 'smooth',
                        block: 'buttom'
                    })*/
                }).catch(err => {
                    this.$toastr.error(err)
                })
            })
        },

        // ── 本地AI大模型翻译 ──────────────────────────────────────────────
        // 状态全部来自 sd_forge_lora_new 的共享服务；lora_new 启用时 frozen=true，
        // 「空闲自动卸载 / 手动卸载」只读（由 lora_new 统一管理，避免两边计时互相卸载）。
        startLLMPolling() {
            this.stopLLMPolling()
            this.llmTimer = setInterval(() => {
                if (!this.isOpen) return
                this.loadLLMStatus()
            }, 5000)
        },
        stopLLMPolling() {
            if (this.llmTimer) {
                clearInterval(this.llmTimer)
                this.llmTimer = null
            }
        },
        applyLLMStatus(st) {
            if (!st) return
            this.llm.available = !!st.ok
            // 后端 installed=false 才是「插件目录不存在」；否则是导入失败
            this.llm.notInstalled = !st.ok && st.installed === false
            this.llm.error = st.ok ? '' : (st.error || '')
            if (!st.ok) return
            this.llm.frozen = !!st.frozen
            this.llm.gpu = !!st.gpu
            this.llm.loaded = !!st.loaded
            this.llm.model = st.model || ''
            this.llm.auto_unload = !!st.auto_unload
            this.llm.idle_minutes = st.idle_minutes || 5
            this.llmIdleMinutes = this.llm.idle_minutes
            this.llmBusy = !!st.busy
            this.llm.note = st.load_error || st.note || ''
            if (st.selected !== undefined && !this.llmSwitching) this.llmSelected = st.selected || ''
        },
        loadLLMStatus() {
            return this.gradioAPI.localLLMStatus().then(res => {
                this.applyLLMStatus(res)
            }).catch(err => {
                // 请求本身失败（后端未启动 / 路由未注册）也要给出可见原因
                this.llm.available = false
                this.llm.notInstalled = false
                this.llm.error = (err && err.message) || String(err)
            })
        },
        refreshLLM() {
            if (this.llmLoading) return
            this.llmLoading = true
            return this.gradioAPI.localLLMModels().then(res => {
                this.llmLoading = false
                if (!res || !res.ok) {
                    this.applyLLMStatus(res)
                    return
                }
                this.llm.available = true
                this.llm.notInstalled = false
                this.llm.error = ''
                this.llmModels = res.models || []
                this.llmSelected = res.selected || ''
                this.llm.gpu = !!res.gpu
                this.llm.cuda_available = !!res.cuda_available
                this.llm.engine_ready = !!res.engine_ready
                this.llm.frozen = !!res.frozen
                this.llm.loaded = !!res.loaded
                this.llm.model = res.loaded || ''
                if (!this.llm.runtime) this.loadLLMRuntime()
            }).catch(err => {
                this.llmLoading = false
                this.$toastr.error(err.message)
            })
        },
        loadLLMRuntime(force = false) {
            return this.gradioAPI.localLLMRuntimeInfo(force).then(res => {
                if (res && res.ok) {
                    this.llm.runtime = res
                    this.llm.engine_ready = !!res.usable
                    this.llm.cuda_available = res.build === 'cuda'
                }
            }).catch(() => {})
        },
        onLLMModelChange(e) {
            const rel = e.target.value
            this.llmSelected = rel
            this.llmSwitching = true
            this.llm.note = ''
            return this.gradioAPI.localLLMSelect(rel).then(res => {
                this.llmSwitching = false
                if (!res || !res.ok) {
                    this.$toastr.error((res && res.error) || 'Failed to select model')
                    return this.loadLLMStatus()
                }
                this.llmSelected = res.selected || ''
                return this.loadLLMStatus()
            }).catch(err => {
                this.llmSwitching = false
                this.$toastr.error(err.message)
            })
        },
        onLLMGpuChange(want) {
            if (this.llm.gpu === want) return
            this.llmSwitching = true
            return this.gradioAPI.localLLMGpu(want).then(res => {
                this.llmSwitching = false
                if (!res || !res.ok) {
                    this.$toastr.error((res && res.error) || 'Failed to switch device')
                    return this.loadLLMStatus()
                }
                this.llm.gpu = !!res.gpu
                return this.loadLLMStatus()
            }).catch(err => {
                this.llmSwitching = false
                this.$toastr.error(err.message)
            })
        },
        onLLMIdleToggle(e) {
            const checked = e.target.checked
            this.llm.auto_unload = checked
            if (this.llm.frozen) return
            return this.gradioAPI.localLLMIdleSettings({auto_unload: checked}).then(res => {
                this.applyLLMStatus(res)
            }).catch(err => {
                this.$toastr.error(err.message)
                return this.loadLLMStatus()
            })
        },
        onLLMIdleMinutesChange() {
            if (this.llm.frozen) return
            let minutes = parseInt(this.llmIdleMinutes)
            if (isNaN(minutes)) minutes = 5
            minutes = Math.max(3, Math.min(200, minutes))
            this.llmIdleMinutes = minutes
            return this.gradioAPI.localLLMIdleSettings({minutes}).then(res => {
                this.applyLLMStatus(res)
            }).catch(err => {
                this.$toastr.error(err.message)
                return this.loadLLMStatus()
            })
        },
        onLLMUnload() {
            if (!this.llm.loaded || this.llmUnloading) return
            this.llmUnloading = true
            return this.gradioAPI.localLLMUnload().then(res => {
                this.llmUnloading = false
                if (!res || !res.ok) {
                    this.$toastr.error((res && res.error) || 'Failed to unload model')
                    return
                }
                this.applyLLMStatus(res)
            }).catch(err => {
                this.llmUnloading = false
                this.$toastr.error(err.message)
            })
        },
        openLLMFolder() {
            return this.gradioAPI.localLLMOpenFolder().then(res => {
                if (!res || !res.ok) this.$toastr.error((res && res.error) || 'Failed to open folder')
            }).catch(err => {
                this.$toastr.error(err.message)
            })
        },
        // ── AI翻译提示词 ──
        loadLLMPrompt() {
            return this.gradioAPI.localLLMPrompt().then(res => {
                if (!res || !res.ok) return
                this.llmAiPromptDefault = res.default || ''
                this.llmAiPrompt = res.text || res.default || ''
            }).catch(() => {})
        },
        onLLMPromptReset() {
            this.llmPromptMsg = ''
            this.llmAiPrompt = this.llmAiPromptDefault
        },
        onLLMPromptSave() {
            if (this.llmPromptSaving) return
            this.llmPromptSaving = true
            this.llmPromptMsg = ''
            return this.gradioAPI.localLLMPromptSave(this.llmAiPrompt).then(res => {
                this.llmPromptSaving = false
                if (!res || !res.ok) {
                    this.llmPromptMsg = (res && res.error) || this.getLang('llm_prompt_save_failed')
                    return
                }
                this.llmAiPrompt = res.text || ''
                this.llmPromptMsg = this.getLang('llm_prompt_saved')
                this.$toastr.success(this.getLang('llm_prompt_saved'))
            }).catch(err => {
                this.llmPromptSaving = false
                this.llmPromptMsg = err.message
            })
        },
        onLLMDownloadCuda() {
            return this.gradioAPI.localLLMRuntimeDownloadCuda().then(res => {
                if (!res || !res.ok) {
                    this.$toastr.error((res && res.error) || 'Failed to start download')
                    return
                }
                if (res.already) return this.loadLLMRuntime(true)
                this.llm.cudaDownloading = true
                this.pollLLMRuntimeDownload()
            }).catch(err => {
                this.$toastr.error(err.message)
            })
        },
        pollLLMRuntimeDownload() {
            this.gradioAPI.localLLMRuntimeDownloadStatus().then(res => {
                if (!res || !res.ok) {
                    this.llm.cudaDownloading = false
                    return
                }
                if (res.active) {
                    setTimeout(() => this.pollLLMRuntimeDownload(), 2000)
                    return
                }
                this.llm.cudaDownloading = false
                if (res.error) {
                    this.$toastr.error(res.error)
                    return
                }
                if (res.finished) {
                    this.$toastr.success(this.getLang('llm_runtime_downloaded'))
                    this.loadLLMRuntime(true)
                }
            }).catch(() => {
                this.llm.cudaDownloading = false
            })
        },
        onLLMTestClick() {
            if (this.llmTesting) return
            this.llmTestError = ''
            this.llmTranslatedText = ''
            this.llmTesting = true
            let configs = {local_llm: {model: this.llmSelected}}
            this.gradioAPI.translate(this.llmTestText, 'en_US', this.languageCode, 'local_llm', configs).then(res => {
                this.llmTesting = false
                if (!res.success) {
                    this.llmTestError = res.message
                } else {
                    this.llmTranslatedText = res.translated_text
                }
                this.loadLLMStatus()
            }).catch(err => {
                this.llmTesting = false
                this.llmTestError = err.message
            })
        },
    },
}
</script>
