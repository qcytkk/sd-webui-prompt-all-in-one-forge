<template>
    <div class="physton-settings-modal" v-show="visible" @click="onMaskClick">
            <div class="settings-modal-main" @click.stop>
                <div class="settings-modal-header">
                    <div class="settings-modal-title">{{ getLang('setting_desc') }}</div>
                    <div class="settings-modal-header-right">
                        <div class="settings-modal-icon-btn" @click="close">
                            <icon-svg name="close"/>
                        </div>
                    </div>
                </div>
                <div class="settings-modal-body">
                    <div class="settings-modal-tabs">
                        <div v-for="tab in tabs" :key="tab.key"
                             :class="['settings-tab-item', {active: activeTab === tab.key}]"
                             @click="switchTab(tab.key)">
                            <icon-svg class="settings-tab-icon" :name="tab.icon"/>
                            <span class="settings-tab-label">{{ getLang(tab.labelKey) }}</span>
                        </div>
                    </div>
                    <div class="settings-modal-content">
                        <!-- 通用 -->
                        <div v-show="activeTab === 'common'" class="settings-tab-pane">
                            <!-- 分组标题已全部去掉（用户要求）；5 个功能行合并进一个 settings-section，仅靠行间虚线分隔 -->
                            <div class="settings-section">
                                <div class="setting-line">
                                    <div class="line-text">
                                        <div class="line-title">{{ getLang('interface_language') }}</div>
                                    </div>
                                    <div class="line-content">
                                        <select class="language-select" :value="languageCode"
                                                :aria-label="getLang('interface_language')" @change="onLanguageChange">
                                            <option v-for="item in languages" :key="item.code" :value="item.code">
                                                {{ item.code }} - {{ item.name }}
                                            </option>
                                        </select>
                                    </div>
                                </div>
                                <div class="setting-line">
                                    <div class="line-text">
                                        <div class="line-title">{{ getLang('webui_theme') }}</div>
                                        <div class="line-desc">{{ getLang('webui_theme_desc') }}</div>
                                    </div>
                                    <div class="line-content">
                                        <select class="theme-select" :value="theme"
                                                :aria-label="getLang('webui_theme')" @change="onThemeChange">
                                            <option value="dark">{{ getLang('theme_dark') }}</option>
                                            <option value="light">{{ getLang('theme_light') }}</option>
                                        </select>
                                    </div>
                                </div>
                                <!-- 自动填充提示词 -->
                                <div class="setting-line">
                                    <div class="line-text">
                                        <div class="line-title">{{ getLang('auto_fill_title') }}</div>
                                        <div class="line-desc">{{ getLang('auto_input_prompt') }}</div>
                                    </div>
                                    <div class="line-content">
                                        <div class="auto-input-row">
                                            <label class="auto-input-label">{{ getLang('prompt') }}:</label>
                                            <select v-model="autoInputPromptPrompt"
                                                    :aria-label="getLang('auto_input_prompt') + ' - ' + getLang('prompt')"
                                                    @change="onAutoInputPromptChange('Prompt', $event.target.value)">
                                                <option value="disabled">{{ getLang('disabled') }}</option>
                                                <option value="last">{{ getLang('last_input_prompt') }}</option>
                                                <optgroup v-for="(item) in getFavoritesByType('prompt')" :key="item.key"
                                                          :label="getLang('favorite') + ' / ' + getLang(item.name)">
                                                    <option v-for="(favorite) in item.list" :value="favorite.id">
                                                        {{ favorite.name || favorite.prompt.substring(0, 40) }}
                                                    </option>
                                                </optgroup>
                                            </select>
                                        </div>
                                        <div class="auto-input-row">
                                            <label class="auto-input-label">{{ getLang('negative_prompt') }}:</label>
                                            <select v-model="autoInputPromptNegative"
                                                    :aria-label="getLang('auto_input_prompt') + ' - ' + getLang('negative_prompt')"
                                                    @change="onAutoInputPromptChange('Negative Prompt', $event.target.value)">
                                                <option value="disabled">{{ getLang('disabled') }}</option>
                                                <option value="last">{{ getLang('last_input_prompt') }}</option>
                                                <optgroup v-for="(item) in getFavoritesByType('negative_prompt')" :key="item.key"
                                                          :label="getLang('favorite') + ' / ' + getLang(item.name)">
                                                    <option v-for="(favorite) in item.list" :value="favorite.id">
                                                        {{ favorite.name || favorite.prompt.substring(0, 40) }}
                                                    </option>
                                                </optgroup>
                                            </select>
                                        </div>
                                    </div>
                                </div>
                                <!-- 输入新关键词后自动翻译（原位于「翻译接口」标签页，按要求移入「通用设置」） -->
                                <div v-if="!isEnglish" class="settings-auto-translate-row">
                                    <div class="line-text">
                                        <div class="line-title">{{ getLang('auto_translation') }}</div>
                                        <div class="line-desc">{{ getLang('auto_translate') }}</div>
                                    </div>
                                    <div class="line-content">
                                        <template v-if="canOneTranslate">
                                            <div class="paio-pill" role="radiogroup" :aria-label="getLang('auto_translate')">
                                                <label class="paio-pill-btn">
                                                    <input class="paio-pill-input" type="radio" name="paio-auto-translate"
                                                           :checked="!autoTranslate"
                                                           @change="$emit('update:autoTranslate', false)">
                                                    <span>{{ getLang('toggle_off') }}</span>
                                                </label>
                                                <label class="paio-pill-btn">
                                                    <input class="paio-pill-input" type="radio" name="paio-auto-translate"
                                                           :checked="autoTranslate"
                                                           @change="$emit('update:autoTranslate', true)">
                                                    <span>{{ getLang('toggle_on') }}</span>
                                                </label>
                                            </div>
                                        </template>
                                        <template v-else>
                                            <div class="paio-pill-group">
                                                <span class="paio-pill-label">{{ getLang('auto_translate_to_local_language') }}</span>
                                                <div class="paio-pill" role="radiogroup" :aria-label="getLang('auto_translate_to_local_language')">
                                                    <label class="paio-pill-btn">
                                                        <input class="paio-pill-input" type="radio" name="paio-auto-translate-local"
                                                               :checked="!autoTranslateToLocal"
                                                               @change="$emit('update:autoTranslateToLocal', false)">
                                                        <span>{{ getLang('toggle_off') }}</span>
                                                    </label>
                                                    <label class="paio-pill-btn">
                                                        <input class="paio-pill-input" type="radio" name="paio-auto-translate-local"
                                                               :checked="autoTranslateToLocal"
                                                               @change="$emit('update:autoTranslateToLocal', true)">
                                                        <span>{{ getLang('toggle_on') }}</span>
                                                    </label>
                                                </div>
                                            </div>
                                            <div class="paio-pill-group">
                                                <span class="paio-pill-label">{{ getLang('auto_translate_to_english') }}</span>
                                                <div class="paio-pill" role="radiogroup" :aria-label="getLang('auto_translate_to_english')">
                                                    <label class="paio-pill-btn">
                                                        <input class="paio-pill-input" type="radio" name="paio-auto-translate-english"
                                                               :checked="!autoTranslateToEnglish"
                                                               @change="$emit('update:autoTranslateToEnglish', false)">
                                                        <span>{{ getLang('toggle_off') }}</span>
                                                    </label>
                                                    <label class="paio-pill-btn">
                                                        <input class="paio-pill-input" type="radio" name="paio-auto-translate-english"
                                                               :checked="autoTranslateToEnglish"
                                                               @change="$emit('update:autoTranslateToEnglish', true)">
                                                        <span>{{ getLang('toggle_on') }}</span>
                                                    </label>
                                                </div>
                                            </div>
                                        </template>
                                    </div>
                                </div>
                                <!-- 功能提示框（按要求移到「自动翻译」之后） -->
                                <div class="setting-line">
                                    <div class="line-text">
                                        <div class="line-title">{{ getLang('tooltip_switch') }}</div>
                                        <div class="line-desc">{{ getLang('whether_to_enable_tooltip') }}</div>
                                    </div>
                                    <div class="line-content">
                                        <div class="paio-pill" role="radiogroup" :aria-label="getLang('tooltip_switch')">
                                            <label class="paio-pill-btn">
                                                <input class="paio-pill-input" type="radio" name="paio-enable-tooltip"
                                                       :checked="!enableTooltip"
                                                       @change="$emit('update:enableTooltip', false)">
                                                <span>{{ getLang('toggle_off') }}</span>
                                            </label>
                                            <label class="paio-pill-btn">
                                                <input class="paio-pill-input" type="radio" name="paio-enable-tooltip"
                                                       :checked="enableTooltip"
                                                       @change="$emit('update:enableTooltip', true)">
                                                <span>{{ getLang('toggle_on') }}</span>
                                            </label>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <!-- 功能区一：隐藏默认输入框（原为主界面工具栏的图标开关，按要求移入；按提示词框各自独立） -->
                            <div class="settings-section">
                                <div class="settings-section-title" role="heading" aria-level="3">{{ getLang('hide_default_input_box') }}</div>
                                <div class="setting-line" v-for="item in promptItems" :key="'hide-' + item.id">
                                    <div class="line-text">
                                        <div class="line-title">{{ promptLabel(item) }}</div>
                                        <div class="line-desc" v-html="getLang(item.neg ? 'hide_default_input_desc_negative' : 'hide_default_input_desc_positive')"></div>
                                    </div>
                                    <div class="line-content">
                                        <div class="paio-pill" role="radiogroup" :aria-label="promptLabel(item)">
                                            <label class="paio-pill-btn">
                                                <input class="paio-pill-input" type="radio" :name="'paio-hide-' + item.id"
                                                       :checked="!item.hideDefaultInput"
                                                       @change="$emit('update:promptOption', item.id, 'hideDefaultInput', false)">
                                                <span>{{ getLang('toggle_off') }}</span>
                                            </label>
                                            <label class="paio-pill-btn">
                                                <input class="paio-pill-input" type="radio" :name="'paio-hide-' + item.id"
                                                       :checked="item.hideDefaultInput"
                                                       @change="$emit('update:promptOption', item.id, 'hideDefaultInput', true)">
                                                <span>{{ getLang('toggle_on') }}</span>
                                            </label>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <!-- 功能区二：自动加载WebUI提示词变动 -->
                            <div class="settings-section">
                                <div class="settings-section-title" role="heading" aria-level="3">{{ getLang('auto_load_title') }}</div>
                                <div class="setting-line" v-for="item in promptItems" :key="'autoload-' + item.id">
                                    <div class="line-text">
                                        <div class="line-title">{{ promptLabel(item) }}</div>
                                        <div class="line-desc" v-html="getLang(item.neg ? 'auto_load_desc_negative' : 'auto_load_desc_positive')"></div>
                                    </div>
                                    <div class="line-content">
                                        <div class="paio-pill" role="radiogroup" :aria-label="promptLabel(item)">
                                            <label class="paio-pill-btn">
                                                <input class="paio-pill-input" type="radio" :name="'paio-autoload-' + item.id"
                                                       :checked="!item.autoLoadWebuiPrompt"
                                                       @change="$emit('update:promptOption', item.id, 'autoLoadWebuiPrompt', false)">
                                                <span>{{ getLang('toggle_off') }}</span>
                                            </label>
                                            <label class="paio-pill-btn">
                                                <input class="paio-pill-input" type="radio" :name="'paio-autoload-' + item.id"
                                                       :checked="item.autoLoadWebuiPrompt"
                                                       @change="$emit('update:promptOption', item.id, 'autoLoadWebuiPrompt', true)">
                                                <span>{{ getLang('toggle_on') }}</span>
                                            </label>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- 翻译API -->
                        <div v-show="activeTab === 'translate'" class="settings-tab-pane">
                            <translate-setting ref="translateSetting" embedded
                                               :language-code="languageCode"
                                               @update:language-code="$emit('update:languageCode', $event)"
                                               :translate-apis="translateApis" :languages="languages"
                                               @forceUpdate:translateApi="$emit('forceUpdate:translateApi', $event)"
                                               :tag-complete-file="tagCompleteFile"
                                               @update:tag-complete-file="$emit('update:tagCompleteFile', $event)"
                                               :only-csv-on-auto="onlyCsvOnAuto"
                                               @update:only-csv-on-auto="$emit('update:onlyCsvOnAuto', $event)"
                                               :group-tags-translate="groupTagsTranslate"
                                               @update:group-tags-translate="$emit('update:groupTagsTranslate', $event)"
                                               :translate-api="translateApi"
                                               @update:translate-api="$emit('update:translateApi', $event)"/>
                        </div>

                        <!-- 提示词格式 -->
                        <div v-show="activeTab === 'format'" class="settings-tab-pane">
                            <prompt-format ref="promptFormat" embedded
                                           :language-code="languageCode"
                                           @update:language-code="$emit('update:languageCode', $event)"
                                           :translate-apis="translateApis"
                                           :languages="languages"
                                           :auto-remove-space="autoRemoveSpace"
                                           @update:auto-remove-space="$emit('update:autoRemoveSpace', $event)"
                                           :auto-remove-last-comma="autoRemoveLastComma"
                                           @update:auto-remove-last-comma="$emit('update:autoRemoveLastComma', $event)"
                                           :auto-keep-weight-zero="autoKeepWeightZero"
                                           @update:auto-keep-weight-zero="$emit('update:autoKeepWeightZero', $event)"
                                           :auto-keep-weight-one="autoKeepWeightOne"
                                           @update:auto-keep-weight-one="$emit('update:autoKeepWeightOne', $event)"
                                           :auto-break-before-wrap="autoBreakBeforeWrap"
                                           @update:auto-break-before-wrap="$emit('update:autoBreakBeforeWrap', $event)"
                                           :auto-break-after-wrap="autoBreakAfterWrap"
                                           @update:auto-break-after-wrap="$emit('update:autoBreakAfterWrap', $event)"
                                           :auto-remove-lora-before-comma="autoRemoveLoraBeforeComma"
                                           @update:auto-remove-lora-before-comma="$emit('update:autoRemoveLoraBeforeComma', $event)"
                                           :auto-remove-lora-after-comma="autoRemoveLoraAfterComma"
                                           @update:auto-remove-lora-after-comma="$emit('update:autoRemoveLoraAfterComma', $event)"
                                           :use-novel-ai-weight-symbol="useNovelAiWeightSymbol"
                                           @update:use-novel-ai-weight-symbol="$emit('update:useNovelAiWeightSymbol', $event)"
                                           :auto-remove-before-line-comma="autoRemoveBeforeLineComma"
                                           @update:auto-remove-before-line-comma="$emit('update:autoRemoveBeforeLineComma', $event)"
                                           :auto-split-by-period="autoSplitByPeriod"
                                           @update:auto-split-by-period="$emit('update:autoSplitByPeriod', $event)"
                                           :auto-split-by-period-include-paren="autoSplitByPeriodIncludeParen"
                                           @update:auto-split-by-period-include-paren="$emit('update:autoSplitByPeriodIncludeParen', $event)"/>
                        </div>

                        <!-- 黑名单 -->
                        <div v-show="activeTab === 'blacklist'" class="settings-tab-pane">
                            <blacklist ref="blacklist" embedded
                                       :language-code="languageCode"
                                       @update:language-code="$emit('update:languageCode', $event)"
                                       :translate-apis="translateApis"
                                       :languages="languages"
                                       :blacklist="blacklist"
                                       :cancel-blacklist-confirm="cancelBlacklistConfirm"
                                       @update:blacklist="$emit('update:blacklist', $event)"/>
                        </div>

                        <!-- 热键 -->
                        <div v-show="activeTab === 'hotkey'" class="settings-tab-pane">
                            <hotkey ref="hotkey" embedded
                                    :language-code="languageCode"
                                    @update:language-code="$emit('update:languageCode', $event)"
                                    :translate-apis="translateApis"
                                    :languages="languages"
                                    :default-hotkey="hotkey"
                                    @update:hotkey="$emit('update:hotkey', $event)"/>
                        </div>

                        <!-- 主题 -->
                        <div v-show="activeTab === 'theme'" class="settings-tab-pane">
                            <extension-css ref="extensionCss" embedded
                                           :language-code="languageCode"
                                           @update:language-code="$emit('update:languageCode', $event)"
                                           :translate-apis="translateApis" :languages="languages"/>
                        </div>

                        <!-- 关于 -->
                        <div v-show="activeTab === 'about'" class="settings-tab-pane">
                            <about ref="about" embedded
                                   :language-code="languageCode"
                                   @update:language-code="$emit('update:languageCode', $event)"
                                   :translate-apis="translateApis" :languages="languages"/>
                        </div>
                    </div>
                </div>
            </div>
        </div>
</template>

<script>
import LanguageMixin from "@/mixins/languageMixin";
import IconSvg from "@/components/iconSvg.vue";
import TranslateSetting from "@/components/translateSetting.vue";
import PromptFormat from "@/components/promptFormat.vue";
import Blacklist from "@/components/blacklist.vue";
import Hotkey from "@/components/hotkey.vue";
import ExtensionCss from "@/components/extensionCss.vue";
import About from "@/components/about.vue";
import GradioAPI from "@/utils/gradioAPI.js";

export default {
    name: 'SettingsModal',
    components: {
        IconSvg, TranslateSetting, PromptFormat, Blacklist, Hotkey, ExtensionCss, About
    },
    mixins: [LanguageMixin],
    props: {
        visible: {type: Boolean, default: false},
        theme: {type: String, default: 'dark'},
        languageCode: {type: String, default: 'en'},
        translateApis: {type: Array, default: () => []},
        languages: {type: Array, default: () => []},
        promptItems: {type: Array, default: () => []},
        canOneTranslate: {type: Boolean, default: false},
        autoTranslate: {type: Boolean, default: false},
        autoTranslateToLocal: {type: Boolean, default: false},
        autoTranslateToEnglish: {type: Boolean, default: false},
        enableTooltip: {type: Boolean, default: true},
        translateApi: {type: [String, Object], default: ''},
        tagCompleteFile: {type: String, default: ''},
        onlyCsvOnAuto: {type: Boolean, default: false},
        groupTagsTranslate: {type: Boolean, default: false},
        autoRemoveSpace: {type: Boolean, default: false},
        autoRemoveLastComma: {type: Boolean, default: false},
        autoKeepWeightZero: {type: Boolean, default: false},
        autoKeepWeightOne: {type: Boolean, default: false},
        autoBreakBeforeWrap: {type: Boolean, default: false},
        autoBreakAfterWrap: {type: Boolean, default: false},
        autoRemoveLoraBeforeComma: {type: Boolean, default: false},
        autoRemoveLoraAfterComma: {type: Boolean, default: false},
        useNovelAiWeightSymbol: {type: Boolean, default: false},
        autoRemoveBeforeLineComma: {type: Boolean, default: false},
        autoSplitByPeriod: {type: Boolean, default: false},
        autoSplitByPeriodIncludeParen: {type: Boolean, default: false},
        blacklist: {type: Object, default: () => ({})},
        cancelBlacklistConfirm: {type: Boolean, default: false},
        hotkey: {type: Array, default: () => []},
    },
    emits: [
        'update:visible', 'update:theme', 'update:languageCode',
        'update:promptOption',
        'update:autoTranslate', 'update:autoTranslateToLocal', 'update:autoTranslateToEnglish',
        'update:enableTooltip', 'update:translateApi', 'update:tagCompleteFile',
        'update:onlyCsvOnAuto', 'update:groupTagsTranslate',
        'update:autoRemoveSpace', 'update:autoRemoveLastComma', 'update:autoKeepWeightZero',
        'update:autoKeepWeightOne', 'update:autoBreakBeforeWrap', 'update:autoBreakAfterWrap',
        'update:autoRemoveLoraBeforeComma', 'update:autoRemoveLoraAfterComma',
        'update:useNovelAiWeightSymbol', 'update:autoRemoveBeforeLineComma',
        'update:autoSplitByPeriod', 'update:autoSplitByPeriodIncludeParen',
        'update:blacklist', 'update:hotkey',
        'forceUpdate:translateApi',
    ],
    data() {
        return {
            activeTab: 'common',
            tabs: [
                {key: 'common', icon: 'setting', labelKey: 'setting'},
                {key: 'translate', icon: 'api', labelKey: 'translate_api'},
                {key: 'format', icon: 'format', labelKey: 'prompt_format'},
                {key: 'blacklist', icon: 'blacklist', labelKey: 'keywords_blacklist'},
                {key: 'hotkey', icon: 'hotkey', labelKey: 'hotkey_setting'},
                {key: 'theme', icon: 'theme', labelKey: 'theme_extension'},
                {key: 'about', icon: 'about', labelKey: 'about_desc'},
            ],
            openedTabs: {},
            autoInputPromptPrompt: 'disabled',
            autoInputPromptNegative: 'disabled',
        }
    },
    computed: {
        isEnglish() {
            return this.languageCode === 'en' || this.languageCode === 'en_US' || this.languageCode === 'en_GB'
        }
    },
    watch: {
        visible(val) {
            if (val) {
                this.loadAutoInputPrompts()
                this.$nextTick(() => this.openTab(this.activeTab))
            } else {
                this.openedTabs = {}
            }
        }
    },
    created() {
        this.gradioAPI = new GradioAPI()
    },
    methods: {
        close() {
            this.$emit('update:visible', false)
        },
        onMaskClick() {
            this.close()
        },
        switchTab(key) {
            if (this.activeTab === key) return
            const oldRef = this.getTabRef(this.activeTab)
            if (oldRef && oldRef.isOpen) oldRef.isOpen = false
            this.activeTab = key
            this.$nextTick(() => this.openTab(key))
        },
        openTab(key) {
            const ref = this.getTabRef(key)
            if (!ref) return
            if (key === 'translate' && !ref.isOpen) {
                ref.open(this.translateApi)
            } else if (!ref.isOpen) {
                ref.open()
            }
            this.openedTabs[key] = true
        },
        getTabRef(key) {
            switch (key) {
                case 'translate': return this.$refs.translateSetting
                case 'format': return this.$refs.promptFormat
                case 'blacklist': return this.$refs.blacklist
                case 'hotkey': return this.$refs.hotkey
                case 'theme': return this.$refs.extensionCss
                case 'about': return this.$refs.about
                default: return null
            }
        },
        loadAutoInputPrompts() {
            this.gradioAPI.getData('autoInputPrompt-Prompt').then(res => {
                if (res !== null && res !== undefined) this.autoInputPromptPrompt = res
            }).catch(() => {})
            this.gradioAPI.getData('autoInputPrompt-Negative Prompt').then(res => {
                if (res !== null && res !== undefined) this.autoInputPromptNegative = res
            }).catch(() => {})
        },
        onAutoInputPromptChange(name, value) {
            this.gradioAPI.setData('autoInputPrompt-' + name, value).then(() => {
                this.$toastr.success(this.getLang('success'))
            }).catch(() => {
                this.$toastr.error(this.getLang('failed'))
            })
        },
        onLanguageChange(e) {
            // 界面语言切换（原顶栏「Language」按钮功能移入设置弹窗）
            this.$emit('update:languageCode', e.target.value)
        },
        onThemeChange(e) {
            // WebUI 主题切换（原为弹窗右上角/内容区的太阳月亮图标按钮，改为下拉）
            this.$emit('update:theme', e.target.value)
        },
        promptLabel(item) {
            // 提示词框的显示名，如「文生图 · 提示词」
            const tab = this.getLang(item.tab === 'tab_txt2img' ? 'txt2img' : 'img2img')
            const kind = this.getLang(item.neg ? 'negative_prompt' : 'prompt')
            return tab + ' · ' + kind
        },
        getFavoritesByType(type) {
            const favorites = typeof window.phystonPromptfavorites === 'object' ? window.phystonPromptfavorites : []
            return favorites.filter(item => item.type === type)
        }
    }
}
</script>
