<template>
    <div>
        <template v-for="(item) in prompts" :key="item.name">
            <physton-prompt v-if="item.$textarea" :id="item.id" :ref="item.id" :name="item.name"
                            :neg="item.neg" :textarea="item.$textarea" :steps="item.$steps"
                            v-model:language-code="languageCode"
                            :translate-apis="translateApis" :languages="languages"
                            :history-key="item.historyKey"
                            @click:show-history="onShowHistory(item.id, $event)"
                            :favorite-key="item.favoriteKey"
                            @refresh-favorites="onRefreshFavorites"
                            @click:show-favorite="onShowFavorite(item.id, $event)"
                            v-model:can-one-translate="canOneTranslate"
                            v-model:auto-translate="autoTranslate"
                            v-model:auto-translate-to-english="autoTranslateToEnglish"
                            v-model:auto-translate-to-local="autoTranslateToLocal"
                            v-model:auto-remove-space="autoRemoveSpace"
                            v-model:auto-remove-last-comma="autoRemoveLastComma"
                            v-model:auto-keep-weight-zero="autoKeepWeightZero"
                            v-model:auto-keep-weight-one="autoKeepWeightOne"
                            v-model:auto-break-before-wrap="autoBreakBeforeWrap"
                            v-model:auto-break-after-wrap="autoBreakAfterWrap"
                            v-model:auto-remove-lora-before-comma="autoRemoveLoraBeforeComma"
                            v-model:auto-remove-lora-after-comma="autoRemoveLoraAfterComma"
                            v-model:use-novel-ai-weight-symbol="useNovelAiWeightSymbol"
                            v-model:auto-remove-before-line-comma="autoRemoveBeforeLineComma"
                            v-model:auto-split-by-period="autoSplitByPeriod"
                            v-model:auto-split-by-period-include-paren="autoSplitByPeriodIncludeParen"
                            :hide-default-input="item.hideDefaultInput"
                            @update:hide-default-input="onUpdateHideDefaultInput(item.id, $event)"
                            :auto-load-webui-prompt="item.autoLoadWebuiPrompt"
                            @update:auto-load-webui-prompt="onUpdateAutoLoadWebuiPrompt(item.id, $event)"
                            :hide-panel="item.hidePanel"
                            @update:hide-panel="onUpdateHidePanel(item.id, $event)"
                            v-model:enable-tooltip="enableTooltip"
                            v-model:show-chatgpt-btn="showChatgptBtn"
                            v-model:show-dedupe-btn="showDedupeBtn"
                            v-model:translate-api="translateApi"
                            :translate-api-config="translateApiConfig"
                            @click:open-settings="onOpenSettings"
                            v-model:tag-complete-file="tagCompleteFile"
                            v-model:only-csv-on-auto="onlyCsvOnAuto"
                            v-model:group-tags-translate="groupTagsTranslate"
                            :translate-flow="translateFlow"
                            @click:select-language="onSelectLanguageClick"
                            @click:show-chatgpt="onShowChatgpt(item.id, $event)"
                            :extra-networks="extraNetworks"
                            :loras="loras"
                            :lycos="lycos"
                            :embeddings="embeddings"
                            :version="version"
                            :latest-version="latestVersion"
                            :is-latest-version="isLatestVersion"
                            :theme="theme"
                            :group-tags="groupTags"
                            :hide-group-tags="item.hideGroupTags"
                            v-model:group-tags-color="groupTagsColor"
                            :group-tags-color-key-cache="groupTagsColorKeyCache"
                            @update:hide-group-tags="onUpdateHideGroupTags(item.id, $event)"
                            :group-tags-translate-cache="groupTagsTranslateCache"
                            v-model:extra-networks-width="extraNetworksWidth"
                            v-model:extra-networks-height="extraNetworksHeight"
                            :blacklist="blacklist"
                            :cancel-blacklist-confirm="cancelBlacklistConfirm"
                            @update:blacklist="onUpdateBlacklist"
                            :hotkey="hotkey"
                            @show-extra-networks="onShowExtraNetworks"
                            @hide-extra-networks="onHideExtraNetworks"
                            @refresh-extra-networks="onRefreshExtraNetworks"
            ></physton-prompt>
        </template>
        <settings-modal ref="settingsModal" v-model:visible="settingsVisible"
                        :theme="theme"
                        @update:theme="onSwitchTheme"
                        v-model:language-code="languageCode"
                        :translate-apis="translateApis" :languages="languages"
                        :can-one-translate="canOneTranslate"
                        v-model:auto-translate="autoTranslate"
                        v-model:auto-translate-to-local="autoTranslateToLocal"
                        v-model:auto-translate-to-english="autoTranslateToEnglish"
                        v-model:enable-tooltip="enableTooltip"
                        v-model:show-chatgpt-btn="showChatgptBtn"
                        v-model:show-dedupe-btn="showDedupeBtn"
                        v-model:translate-api="translateApi"
                        v-model:tag-complete-file="tagCompleteFile"
                        v-model:only-csv-on-auto="onlyCsvOnAuto"
                        v-model:group-tags-translate="groupTagsTranslate"
                        v-model:translate-flow="translateFlow"
                        v-model:auto-remove-space="autoRemoveSpace"
                        v-model:auto-remove-last-comma="autoRemoveLastComma"
                        v-model:auto-keep-weight-zero="autoKeepWeightZero"
                        v-model:auto-keep-weight-one="autoKeepWeightOne"
                        v-model:auto-break-before-wrap="autoBreakBeforeWrap"
                        v-model:auto-break-after-wrap="autoBreakAfterWrap"
                        v-model:auto-remove-lora-before-comma="autoRemoveLoraBeforeComma"
                        v-model:auto-remove-lora-after-comma="autoRemoveLoraAfterComma"
                        v-model:use-novel-ai-weight-symbol="useNovelAiWeightSymbol"
                        v-model:auto-remove-before-line-comma="autoRemoveBeforeLineComma"
                        v-model:auto-split-by-period="autoSplitByPeriod"
                        v-model:auto-split-by-period-include-paren="autoSplitByPeriodIncludeParen"
                        :blacklist="blacklist"
                        :cancel-blacklist-confirm="cancelBlacklistConfirm"
                        @update:blacklist="onUpdateBlacklist"
                        :hotkey="hotkey"
                        @update:hotkey="onUpdateHotkey"
                        :prompt-items="prompts"
                        @update:prompt-option="onUpdatePromptOption"
                        @forceUpdate:translateApi="updateTranslateApiConfig"/>
        <select-language ref="selectLanguage" v-model:language-code="languageCode"
                         :translate-apis="translateApis"
                         :languages="languages"
                         v-model:translate-api="translateApi"
                         v-model:tag-complete-file="tagCompleteFile"
                         v-model:only-csv-on-auto="onlyCsvOnAuto"></select-language>
        <history ref="history" v-model:language-code="languageCode"
                 :translate-apis="translateApis" :languages="languages"
                 v-model:tag-complete-file="tagCompleteFile"
                 v-model:only-csv-on-auto="onlyCsvOnAuto"
                 @refresh-favorites="onRefreshFavorites"
                 @use="onUseHistory"/>
        <favorite ref="favorite" v-model:language-code="languageCode"
                  :translate-apis="translateApis" :languages="languages"
                  v-model:tag-complete-file="tagCompleteFile"
                  v-model:only-csv-on-auto="onlyCsvOnAuto"
                  @use="onUseFavorite"></favorite>
        <packages-state ref="packagesState" v-model:language-code="languageCode"
                        :translate-apis="translateApis" :languages="languages"
                        @click:select-language="onSelectLanguageClick"
                        :packages-state="packagesState" :python="python"/>
        <chatgpt-prompt ref="chatgptPrompt" v-model:language-code="languageCode"
                        :translate-apis="translateApis" :languages="languages"
                        @use="onUseChatgpt" />

        <extra-networks-popup ref="extraNetworksPopup"
                              v-model:language-code="languageCode"
                              :translate-apis="translateApis" :languages="languages"
                              :extra-networks="extraNetworks" />

        <div class="physton-paste-popup" v-if="showPastePopup" @click="closePastePopup">
            <div class="paste-popup-main" @click.stop>
                <div class="paste-popup-close" @click="closePastePopup">
                    <icon-svg name="close"/>
                </div>
                <div class="paste-popup-title">{{ pasteTitle }}</div>
                <div class="paste-popup-body">
                    <textarea class="paste-content" v-model="pasteContent"
                              :placeholder="getLang('please_enter_the_content_here')"></textarea>
                    <div v-if="!pasteLoading" class="paste-submit" @click="onClickPasteSubmit">Submit</div>
                    <div v-else class="paste-submit">
                        <icon-svg name="loading"/>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import PhystonPrompt from "./components/phystonPrompt.vue"
import common from "@/utils/common";
import SelectLanguage from "@/components/selectLanguage.vue";
import Favorite from "@/components/favorite.vue";
import History from "@/components/history.vue";
import IconSvg from "@/components/iconSvg.vue";
import PackagesState from "@/components/packagesState.vue";
import ChatgptPrompt from "@/components/chatgptPrompt.vue";
import SettingsModal from "@/components/settingsModal.vue";
import globals from "../globals";
import jsYaml from "js-yaml";
import {ref} from "vue";
import ExtraNetworksPopup from "@/components/extraNetworksPopup.vue";
import waitTick from "@/utils/waitTick";

// 翻译流程支持的五个方案（顺序由用户拖动决定）
const FLOW_KEYS = ['group_tags', 'tag_dict', 'machine_dict', 'network', 'local_llm'];

export default {
    name: 'App',
    components: {
        ChatgptPrompt,
        PackagesState,
        IconSvg,
        History,
        Favorite,
        SelectLanguage,
        SettingsModal,
        PhystonPrompt,
        ExtraNetworksPopup
    },
    mixins: [],
    data() {
        return {
            prompts: [
                {
                    tab: 'tab_txt2img',
                    prompt: 'txt2img_prompt',
                    counter: 'txt2img_token_counter',
                    button: 'txt2img_token_button',
                    steps: 'txt2img_steps',
                    historyKey: 'txt2img',
                    favoriteKey: 'txt2img',
                    $prompt: null,
                    $textarea: null,
                    $steps: null,
                    name: 'txt2img_prompt',
                    neg: false,
                    hideDefaultInputKey: 'txt2ImgHideDefaultInput',
                    hideDefaultInput: false,
                    autoLoadWebuiPromptKey: 'txt2ImgAutoLoadWebuiPrompt',
                    autoLoadWebuiPrompt: true,
                    hidePanelKey: 'txt2ImgHidePanel',
                    hidePanel: false,
                    hideGroupTagsKey: 'txt2ImgHideGroupTags',
                    hideGroupTags: false,
                    id: 'phystonPrompt_txt2img_prompt'
                },
                {
                    tab: 'tab_txt2img',
                    prompt: 'txt2img_neg_prompt',
                    counter: 'txt2img_negative_token_counter',
                    button: 'txt2img_negative_token_button',
                    steps: 'txt2img_steps',
                    historyKey: 'txt2img_neg',
                    favoriteKey: 'txt2img_neg',
                    $prompt: null,
                    $textarea: null,
                    $steps: null,
                    name: 'txt2img_neg_prompt',
                    neg: true,
                    hideDefaultInputKey: 'txt2ImgNegHideDefaultInput',
                    hideDefaultInput: false,
                    autoLoadWebuiPromptKey: 'txt2ImgNegAutoLoadWebuiPrompt',
                    autoLoadWebuiPrompt: true,
                    hidePanelKey: 'txt2ImgNegHidePanel',
                    hidePanel: false,
                    hideGroupTagsKey: 'txt2ImgNegHideGroupTags',
                    hideGroupTags: false,
                    id: 'phystonPrompt_txt2img_neg_prompt'
                },
                {
                    tab: 'tab_img2img',
                    prompt: 'img2img_prompt',
                    counter: 'img2img_token_counter',
                    button: 'img2img_token_button',
                    steps: 'img2img_steps',
                    historyKey: 'img2img',
                    favoriteKey: 'img2img',
                    $prompt: null,
                    $textarea: null,
                    $steps: null,
                    name: 'img2img_prompt',
                    neg: false,
                    hideDefaultInputKey: 'img2ImgHideDefaultInput',
                    hideDefaultInput: false,
                    autoLoadWebuiPromptKey: 'img2ImgAutoLoadWebuiPrompt',
                    autoLoadWebuiPrompt: true,
                    hidePanelKey: 'img2ImgHidePanel',
                    hidePanel: false,
                    hideGroupTagsKey: 'img2ImgHideGroupTags',
                    hideGroupTags: false,
                    id: 'phystonPrompt_img2img_prompt'
                },
                {
                    tab: 'tab_img2img',
                    prompt: 'img2img_neg_prompt',
                    counter: 'img2img_negative_token_counter',
                    button: 'img2img_negative_token_button',
                    steps: 'img2img_steps',
                    historyKey: 'img2img_neg',
                    favoriteKey: 'img2img_neg',
                    $prompt: null,
                    $textarea: null,
                    $steps: null,
                    name: 'img2img_neg_prompt',
                    neg: true,
                    hideDefaultInputKey: 'img2ImgNegHideDefaultInput',
                    hideDefaultInput: false,
                    autoLoadWebuiPromptKey: 'img2ImgNegAutoLoadWebuiPrompt',
                    autoLoadWebuiPrompt: true,
                    hidePanelKey: 'img2ImgNegHidePanel',
                    hidePanel: false,
                    hideGroupTagsKey: 'img2ImgNegHideGroupTags',
                    hideGroupTags: false,
                    id: 'phystonPrompt_img2img_neg_prompt'
                },
            ],
            languageCode: '',
            languages: {},
            translateApis: [],
            translateApi: '',
            translateApiConfig: {},
            canOneTranslate: false,
            autoTranslate: false,
            autoTranslateToEnglish: false,
            autoTranslateToLocal: false,
            autoRemoveSpace: true,
            autoRemoveLastComma: false,
            autoKeepWeightZero: false,
            autoKeepWeightOne: false,
            autoBreakBeforeWrap: false,
            autoBreakAfterWrap: false,
            autoRemoveLoraBeforeComma: false,
            autoRemoveLoraAfterComma: false,
            useNovelAiWeightSymbol: false,
            autoRemoveBeforeLineComma: false,
            autoSplitByPeriod: false,
            autoSplitByPeriodIncludeParen: false,
            // hideDefaultInput: false,
            enableTooltip: true,
            // 【使用Ai生成提示词】按钮的显示开关（主界面工具栏）
            showChatgptBtn: true,
            // 【去除重复的关键词】按钮的显示开关（主界面工具栏）
            showDedupeBtn: true,
            tagCompleteFile: '',
            onlyCsvOnAuto: false,
            // 翻译流程：五个方案的开关与顺序（数组顺序 = 尝试顺序）
            translateFlow: [
                {key: 'group_tags', enabled: true},
                {key: 'tag_dict', enabled: true},
                {key: 'machine_dict', enabled: true},
                {key: 'network', enabled: true},
                {key: 'local_llm', enabled: false},
            ],

            startWatchSave: false,

            pasteBtn: null,
            showPastePopup: false,
            pasteTitle: '',
            pasteContent: '',
            pasteLoading: false,

            historyCurrentPrompt: '',
            favoriteCurrentPrompt: '',
            chatgptCurrentPrompt: '',

            extraNetworks: [],
            loras: [],
            lycos: [],
            embeddings: [],

            python: '',
            packagesState: [],

            version: '',
            latestVersion: '',
            isLatestVersion: true,

            theme: 'dark',

            settingsVisible: false,

            groupTags: [],
            groupTagsColor: {},
            groupTagsColorKeyCache: {},
            groupTagsTranslate: true,
            groupTagsTranslateCache: {
                toEn: new Map(),
                toLocal: new Map()
            },
            extraNetworksWidth: 100,
            extraNetworksHeight: 120,

            blacklist: {},
            cancelBlacklistConfirm: false,

            hotkey: {
                click: 'edit', // edit, disable, extend
                dblClick: 'disable', // edit, disable, extend
                rightClick: '', // edit, disable, extend
                hover: 'extend', // extend
            }
        }
    },
    watch: {
        languageCode: {
            handler: function (val, oldVal) {
                if (!this.startWatchSave) return
                console.log('onLanguageCodeChange', val)
                this.canOneTranslate = common.canOneTranslate(this.languageCode)
                this.gradioAPI.setData('languageCode', val).then(data => {
                }).catch(err => {
                })
                waitTick.addWaitTick(() => this.loadGroupTags())
            },
            immediate: false,
        },
        autoTranslateToEnglish: {
            handler: function (val, oldVal) {
                if (!this.startWatchSave) return
                console.log('onAutoTranslateToEnglishChange', val)
                this.gradioAPI.setData('autoTranslateToEnglish', val).then(data => {
                }).catch(err => {
                })
            },
            immediate: false,
        },
        autoTranslateToLocal: {
            handler: function (val, oldVal) {
                if (!this.startWatchSave) return
                console.log('onAutoTranslateToLocalChange', val)
                this.gradioAPI.setData('autoTranslateToLocal', val).then(data => {
                }).catch(err => {
                })
            },
            immediate: false,
        },
        autoTranslate: {
            handler: function (val, oldVal) {
                if (!this.startWatchSave) return
                this.autoTranslateToEnglish = this.autoTranslate
                this.autoTranslateToLocal = this.autoTranslate
                console.log('onAutoTranslateChange', val)
                this.gradioAPI.setData('autoTranslate', val).then(data => {
                }).catch(err => {
                })
            },
            immediate: false,
        },
        autoRemoveSpace: {
            handler: function (val, oldVal) {
                if (!this.startWatchSave) return
                console.log('onAutoRemoveSpaceChange', val)
                this.gradioAPI.setData('autoRemoveSpace', val).then(data => {
                    this.prompts.forEach(item => {
                        this.$refs[item.id][0].updatePrompt()
                    })
                }).catch(err => {
                })
            },
            immediate: false,
        },
        autoRemoveLastComma: {
            handler: function (val, oldVal) {
                if (!this.startWatchSave) return
                console.log('onAutoRemoveLastCommaChange', val)
                this.gradioAPI.setData('autoRemoveLastComma', val).then(data => {
                    this.prompts.forEach(item => {
                        this.$refs[item.id][0].updatePrompt()
                    })
                }).catch(err => {
                })
            },
            immediate: false,
        },
        autoKeepWeightZero: {
            handler: function (val, oldVal) {
                if (!this.startWatchSave) return
                console.log('onAutoKeepWeightZeroChange', val)
                this.gradioAPI.setData('autoKeepWeightZero', val).then(data => {
                }).catch(err => {
                })
            },
            immediate: false,
        },
        autoKeepWeightOne: {
            handler: function (val, oldVal) {
                if (!this.startWatchSave) return
                console.log('onAutoKeepWeightOneChange', val)
                this.gradioAPI.setData('autoKeepWeightOne', val).then(data => {
                }).catch(err => {
                })
            },
            immediate: false,
        },
        autoBreakBeforeWrap: {
            handler: function (val, oldVal) {
                if (!this.startWatchSave) return
                console.log('onAutoBreakBeforeWrap', val)
                this.gradioAPI.setData('autoBreakBeforeWrap', val).then(data => {
                    this.prompts.forEach(item => {
                        this.$refs[item.id][0].updatePrompt()
                    })
                }).catch(err => {
                })
            },
            immediate: false,
        },
        autoBreakAfterWrap: {
            handler: function (val, oldVal) {
                if (!this.startWatchSave) return
                console.log('onAutoBreakAfterWrap', val)
                this.gradioAPI.setData('autoBreakAfterWrap', val).then(data => {
                    this.prompts.forEach(item => {
                        this.$refs[item.id][0].updatePrompt()
                    })
                }).catch(err => {
                })
            },
            immediate: false,
        },
        autoRemoveLoraBeforeComma: {
            handler: function (val, oldVal) {
                if (!this.startWatchSave) return
                console.log('onAutoRemoveLoraBeforeCommaChange', val)
                this.gradioAPI.setData('autoRemoveLoraBeforeComma', val).then(data => {
                }).catch(err => {
                })
            },
            immediate: false,
        },
        autoRemoveLoraAfterComma: {
            handler: function (val, oldVal) {
                if (!this.startWatchSave) return
                console.log('onAutoRemoveLoraAfterCommaChange', val)
                this.gradioAPI.setData('autoRemoveLoraAfterComma', val).then(data => {
                }).catch(err => {
                })
            },
            immediate: false,
        },
        useNovelAiWeightSymbol: {
            handler: function (val, oldVal) {
                if (!this.startWatchSave) return
                console.log('onUseNovelAiWeightSymbolChange', val)
                this.gradioAPI.setData('useNovelAiWeightSymbol', val).then(data => {
                }).catch(err => {
                })
            },
            immediate: false,
        },
        autoRemoveBeforeLineComma: {
            handler: function (val, oldVal) {
                if (!this.startWatchSave) return
                console.log('onAutoRemoveBeforeLineCommaChange', val)
                this.gradioAPI.setData('autoRemoveBeforeLineComma', val).then(data => {
                }).catch(err => {
                })
            }
        },
        // autoSplitByPeriod：選項變更時，先分割 tags 陣列，再重新產生輸出
        // 原因：僅呼叫 updatePrompt() 只會在輸出字串層級分割，tags 陣列不會被修改，
        // 導致 UI 顯示與輸出不一致。因此需先呼叫 applySplitByPeriod() 同步修改 tags。
        autoSplitByPeriod: {
            handler: function (val, oldVal) {
                if (!this.startWatchSave) return
                console.log('onAutoSplitByPeriodChange', val)
                this.gradioAPI.setData('autoSplitByPeriod', val).then(data => {
                    this.prompts.forEach(item => {
                        this.$refs[item.id][0].applySplitByPeriod()
                        this.$refs[item.id][0].updatePrompt()
                    })
                }).catch(err => {
                })
            },
            immediate: false,
        },
        // autoSplitByPeriodIncludeParen：子選項變更僅重新產生輸出
        // 原因：此選項控制是否允許拆分括號前的 ". "（如 "word1. (test)"）。
        // 由於 tags 已在 autoSplitByPeriod 開啟時被分割，此選項的變更不會影響已分割的 tags，
        // 僅影響後續新載入標籤的分割行為。
        autoSplitByPeriodIncludeParen: {
            handler: function (val, oldVal) {
                if (!this.startWatchSave) return
                console.log('onAutoSplitByPeriodIncludeParenChange', val)
                this.gradioAPI.setData('autoSplitByPeriodIncludeParen', val).then(data => {
                    this.prompts.forEach(item => {
                        this.$refs[item.id][0].updatePrompt()
                    })
                }).catch(err => {
                })
            },
            immediate: false,
        },
        /*hideDefaultInput: {
            handler: function (val, oldVal) {
                if (!this.startWatchSave) return
                console.log('onHideDefaultInputChange', val)
                this.prompts.forEach(item => {
                    item.$prompt.parentElement.parentElement.style.display = val ? 'none' : 'flex'
                })
                this.gradioAPI.setData('hideDefaultInput', val).then(data => {
                }).catch(err => {
                })
            },
            immediate: false,
        },*/
        enableTooltip: {
            handler: function (val, oldVal) {
                if (!this.startWatchSave) return
                localStorage.setItem('phystonPromptEnableTooltip', val ? 'true' : 'false')
                this.updateTippyState()
                this.gradioAPI.setData('enableTooltip', val).then(data => {
                }).catch(err => {
                })
            },
            immediate: false,
        },
        showChatgptBtn: {
            handler: function (val, oldVal) {
                if (!this.startWatchSave) return
                this.gradioAPI.setData('showChatgptBtn', val).then(data => {
                }).catch(err => {
                })
            },
            immediate: false,
        },
        showDedupeBtn: {
            handler: function (val, oldVal) {
                if (!this.startWatchSave) return
                this.gradioAPI.setData('showDedupeBtn', val).then(data => {
                }).catch(err => {
                })
            },
            immediate: false,
        },
        translateApi: {
            handler: function (val, oldVal) {
                if (!this.startWatchSave) return
                console.log('onTranslateApiChange', val, oldVal)
                this.updateTranslateApiConfig()
                this.gradioAPI.setData('translateApi', val).then(data => {
                }).catch(err => {
                })
            },
            immediate: false,
        },
        tagCompleteFile: {
            handler: function (val, oldVal) {
                if (!this.startWatchSave) return
                console.log('onTagCompleteFileChange', val, oldVal)
                this.gradioAPI.setData('tagCompleteFile', val).then(data => {
                }).catch(err => {
                })
            },
            immediate: false,
        },
        groupTagsColor: {
            handler: function (val, oldVal) {
                if (!this.startWatchSave) return
                console.log('onGroupTagsColorChange', val, oldVal)
                this.gradioAPI.setData('groupTagsColor', val).then(data => {
                }).catch(err => {
                })
            },
            deep: true,
            immediate: false,
        },
        groupTagsTranslate: {
            handler: function (val, oldVal) {
                if (!this.startWatchSave) return
                console.log('onGroupTagsTranslateChange', val, oldVal)
                this.gradioAPI.setData('groupTagsTranslate', val).then(data => {
                }).catch(err => {
                })
            },
            immediate: false,
        },
        onlyCsvOnAuto() {
            if (!this.startWatchSave) return
            console.log('onOnlyCsvOnAutoChange', this.onlyCsvOnAuto)
            this.gradioAPI.setData('onlyCsvOnAuto', this.onlyCsvOnAuto).then(data => {
            }).catch(err => {
            })
        },
        translateFlow: {
            handler: function (val, oldVal) {
                if (!this.startWatchSave) return
                console.log('onTranslateFlowChange', val, oldVal)
                this.gradioAPI.setData('translateFlow', val).then(data => {
                }).catch(err => {
                })
            },
            deep: true,
            immediate: false,
        },
        extraNetworksWidth() {
            if (!this.startWatchSave) return
            if (this.extraNetworksWidthTimer) clearTimeout(this.extraNetworksWidthTimer)
            this.extraNetworksWidthTimer = setTimeout(() => {
                console.log('onExtraNetworksWidthChange', this.extraNetworksWidth)
                this.gradioAPI.setData('extraNetworksWidth', this.extraNetworksWidth).then(data => {
                }).catch(err => {
                })
            }, 500)
        },
        extraNetworksHeight() {
            if (!this.startWatchSave) return
            if (this.extraNetworksHeightTimer) clearTimeout(this.extraNetworksHeightTimer)
            this.extraNetworksHeightTimer = setTimeout(() => {
                console.log('onExtraNetworksHeightChange', this.extraNetworksHeight)
                this.gradioAPI.setData('extraNetworksHeight', this.extraNetworksHeight).then(data => {
                }).catch(err => {
                })
            }, 500)
        },
    },
    mounted() {
        const urlParams = new URLSearchParams(window.location.search);
        let theme = urlParams.get("__theme")
        if (['dark', 'light'].includes(theme)) {
            this.theme = theme
            if (!common.gradioApp().classList.contains(this.theme)) {
                common.gradioApp().classList.add(this.theme)
            }
        }

        // sd-webui-lobe-theme
        setTimeout(() => {
            let hasLobeTheme = false
            let hasKitchenTheme = false
            if (localStorage.getItem("SD-LOBE-SETTING") || localStorage.getItem("SD-KITCHEN-SETTING") || document.querySelector('head > meta[name="application-name"]')?.content?.includes?.('Lobe')) {
                let links = document.getElementsByTagName('link')
                for (let i = 0; i < links.length; i++) {
                    let link = links[i]
                    if (link.href.includes('lobehub/')) {
                        hasLobeTheme = true
                        break
                    } else if (link.href.includes('kitchen-theme')) {
                        hasKitchenTheme = true
                    }
                }
            }
            if (hasLobeTheme) {
                common.gradioApp().classList.add("physton-prompt-lobehub")
            } else if (hasKitchenTheme) {
                common.gradioApp().classList.add("physton-prompt-kitchen")
            }
        }, 3000)


        this.loadConfig()
    },
    methods: {
        /**
         * 拉取后台配置并初始化。
         *
         * 页面脚本会比后端的 on_app_started 回调更早执行（Gradio launch 之后、
         * 各扩展注册路由之前），此时 /physton_prompt/get_config 还是 404，
         * 一次性请求失败会导致插件整块不渲染、必须手动刷新。
         * 这里按 1s 间隔重试，最多 15 次（约 15s），覆盖扩展注册路由的耗时。
         */
        loadConfig(attempt = 0) {
            this.gradioAPI.getConfig().then(res => {
                console.log('config:', res)
                // 样式也等后台路由可用后再加载：启动瞬间 /physton_prompt/styles 还是 404，
                // 提前加载会让 <link> 永久失效，表现为插件样式全丢，只能手动刷新恢复。
                common.loadCSS('toastr.min.css', 'physton-prompt-toastr', true, true, false)
                common.loadCSS('tippy.css', 'physton-prompt-tippy', true, true, false)
                common.loadCSS('vue3-colorpicker.css', 'physton-prompt-vue3-colorpicker', true, true, false)
                common.loadCSS('animate.min.css', 'physton-prompt-animate', true, true, false)
                common.loadCSS('main.min.css', 'physton-prompt-main', true)
                this.languageCode = res.i18n.default
                this.translateApi = res.translate_apis.default
                this.translateApis = res.translate_apis.apis
                this.python = res.python
                this.packagesState = res.packages_state
                let languages = {}
                res.i18n.languages.forEach(lang => {
                    languages[lang.code] = lang
                })
                this.languages = languages
                this.init()
            }).catch(err => {
                if (attempt < 15) {
                    setTimeout(() => this.loadConfig(attempt + 1), 1000)
                    return
                }
                this.$toastr.error("Connection to backend API service failed. Please manually refresh the webpage. If it still doesn't work, please restart the WebUI.<br/>连接到后台接口服务失败，请手动再刷新一次网页。如果还是不行，请重启WebUI。<br/><br/>" + err.message, globals.shortName, {timeOut: 20000})
                console.log(err)
            })
        },
        getLang(key) {
            return common.getLang(key, this.languageCode, this.languages)
        },
        init() {
            this.loadExtraNetworks()
            let dataListsKeys = [
                'languageCode',
                'autoTranslate',
                'autoTranslateToEnglish',
                'autoTranslateToLocal',
                'autoRemoveSpace',
                'autoRemoveLastComma',
                'autoKeepWeightZero',
                'autoKeepWeightOne',
                'autoBreakBeforeWrap',
                'autoBreakAfterWrap',
                'autoRemoveLoraBeforeComma',
                'autoRemoveLoraAfterComma',
                'useNovelAiWeightSymbol',
                'autoRemoveBeforeLineComma',
                'autoSplitByPeriod',
                'autoSplitByPeriodIncludeParen',
                /*'hideDefaultInput', */
                'translateApi',
                'enableTooltip',
                'showChatgptBtn',
                'showDedupeBtn',
                'tagCompleteFile',
                'onlyCsvOnAuto',
                'translateFlow',
                'extensionSelect.minimalist',
                'groupTagsColor',
                'groupTagsTranslate',
                'blacklist',
                'cancelBlacklistConfirm',
                'hotkey',
                'extraNetworksWidth',
                'extraNetworksHeight',
            ]
            this.prompts.forEach(item => {
                dataListsKeys.push(item.hideDefaultInputKey)
                dataListsKeys.push(item.autoLoadWebuiPromptKey)
                dataListsKeys.push(item.hidePanelKey)
                dataListsKeys.push(item.hideGroupTagsKey)
            })

            this.gradioAPI.getDatas(dataListsKeys).then(data => {
                if (data.languageCode !== null) {
                    let findLang = false
                    for (let key in this.languages) {
                        if (this.languages[key].code === data.languageCode) {
                            findLang = true
                            break
                        }
                    }
                    if (findLang) {
                        this.languageCode = data.languageCode
                        this.$forceUpdate()
                        this.gradioAPI.setData('languageCode', this.languageCode)
                    }
                } else {
                    let browserLang = navigator.language || navigator.userLanguage || ''
                    if (browserLang) {
                        for (let key in this.languages) {
                            if (common.isSameLang(this.languages[key].code, browserLang)) {
                                this.languageCode = this.languages[key].code
                                this.$forceUpdate()
                                this.gradioAPI.setData('languageCode', this.languageCode)
                                break
                            }
                        }
                    }
                }
                this.canOneTranslate = common.canOneTranslate(this.languageCode)
                if (data.autoTranslateToEnglish !== null) {
                    this.autoTranslateToEnglish = data.autoTranslateToEnglish
                }
                if (data.autoTranslateToLocal !== null) {
                    this.autoTranslateToLocal = data.autoTranslateToLocal
                }
                if (data.autoTranslate !== null) {
                    if (this.canOneTranslate) {
                        this.autoTranslate = data.autoTranslate
                        this.autoTranslateToEnglish = this.autoTranslate
                        this.autoTranslateToLocal = this.autoTranslate
                    } else {
                        this.autoTranslate = false
                    }
                } else {
                    if (this.canOneTranslate) {
                        this.autoTranslate = this.autoTranslateToEnglish || this.autoTranslateToLocal
                        this.autoTranslateToEnglish = true
                        this.autoTranslateToLocal = true
                    } else {
                        this.autoTranslate = false
                    }
                }
                if (data.autoRemoveSpace !== null) {
                    this.autoRemoveSpace = data.autoRemoveSpace
                }
                if (data.autoRemoveLastComma !== null) {
                    this.autoRemoveLastComma = data.autoRemoveLastComma
                }
                if (data.autoKeepWeightZero !== null) {
                    this.autoKeepWeightZero = data.autoKeepWeightZero
                }
                if (data.autoKeepWeightOne !== null) {
                    this.autoKeepWeightOne = data.autoKeepWeightOne
                }
                if (data.autoBreakBeforeWrap !== null) {
                    this.autoBreakBeforeWrap = data.autoBreakBeforeWrap
                }
                if (data.autoBreakAfterWrap !== null) {
                    this.autoBreakAfterWrap = data.autoBreakAfterWrap
                }
                if (data.autoRemoveLoraBeforeComma !== null) {
                    this.autoRemoveLoraBeforeComma = data.autoRemoveLoraBeforeComma
                }
                if (data.autoRemoveLoraAfterComma !== null) {
                    this.autoRemoveLoraAfterComma = data.autoRemoveLoraAfterComma
                }
                if (data.useNovelAiWeightSymbol !== null) {
                    this.useNovelAiWeightSymbol = data.useNovelAiWeightSymbol
                }
                if (data.autoRemoveBeforeLineComma !== null) {
                    this.autoRemoveBeforeLineComma = data.autoRemoveBeforeLineComma
                }
                if (data.autoSplitByPeriod !== null) {
                    this.autoSplitByPeriod = data.autoSplitByPeriod
                }
                if (data.autoSplitByPeriodIncludeParen !== null) {
                    this.autoSplitByPeriodIncludeParen = data.autoSplitByPeriodIncludeParen
                }
                /*if (data.hideDefaultInput !== null) {
                    this.hideDefaultInput = data.hideDefaultInput
                }*/
                if (data.enableTooltip !== null) {
                    this.enableTooltip = data.enableTooltip
                }
                localStorage.setItem('phystonPromptEnableTooltip', this.enableTooltip ? 'true' : 'false')
                this.updateTippyState()
                if (data.showChatgptBtn !== null) {
                    this.showChatgptBtn = data.showChatgptBtn
                }
                if (data.showDedupeBtn !== null) {
                    this.showDedupeBtn = data.showDedupeBtn
                }
                if (data.translateApi !== null) {
                    this.translateApi = data.translateApi
                    /*if (data.translateApi === 'alibaba_free') {
                        this.gradioAPI.setData('translateApi', this.translateApi)
                    } else {
                        this.translateApi = data.translateApi
                    }*/
                }
                if (data.tagCompleteFile !== null) {
                    this.tagCompleteFile = data.tagCompleteFile
                    waitTick.addWaitTick(() => {
                        this.$refs.settingsModal.$refs.translateSetting.getCSV(this.tagCompleteFile)
                    })
                } else {
                    /*if (typeof TAC_CFG === 'object' && typeof QUEUE_FILE_LOAD === 'object') {
                        QUEUE_FILE_LOAD.push(() => {
                            if (typeof TAC_CFG.translation !== 'object' || typeof TAC_CFG.translation.translationFile !== 'string') return
                            if (!TAC_CFG.translation.translationFile) return
                            this.tagCompleteFile = '\\extensions\\a1111-sd-webui-tagcomplete\\tags\\' + TAC_CFG.translation.translationFile
                            this.$refs.translateSetting.getCSV(this.tagCompleteFile)
                        })
                    }*/
                }
                if (data.onlyCsvOnAuto !== null) {
                    this.onlyCsvOnAuto = data.onlyCsvOnAuto
                }

                if (Array.isArray(data.translateFlow) && data.translateFlow.length) {
                    // 兼容：只保留已知的 5 个 key，缺失项按默认顺序插回原位置
                    // （老数据没有【机翻词典】时，它会落在【连网翻译】之前 = 先查缓存再联网）
                    const saved = data.translateFlow.filter(item => item && FLOW_KEYS.includes(item.key))
                        .map(item => ({key: item.key, enabled: !!item.enabled}))
                    FLOW_KEYS.forEach((key, defaultIndex) => {
                        if (saved.some(item => item.key === key)) return
                        const def = this.translateFlow.find(item => item.key === key) || {enabled: false}
                        let insertAt = saved.length
                        for (let i = 0; i < saved.length; i++) {
                            if (FLOW_KEYS.indexOf(saved[i].key) > defaultIndex) {
                                insertAt = i
                                break
                            }
                        }
                        saved.splice(insertAt, 0, {key, enabled: !!def.enabled})
                    })
                    this.translateFlow = saved
                }

                // 旧数据迁移：以前 local_llm 是「翻译接口」里的一个选项，
                // 现在它只能在【翻译流程】里开关，接口下拉不再提供它。
                if (this.translateApi === 'local_llm') {
                    this.translateFlow = this.translateFlow.map(item => (
                        item.key === 'local_llm' ? {key: item.key, enabled: true} : item
                    ))
                    this.translateApi = 'bing_free'
                }

                if (data['extensionSelect.minimalist'] === null) {
                    this.gradioAPI.setData('extensionSelect.minimalist', true)
                }

                if (data.groupTagsColor !== null) {
                    if (typeof data.groupTagsColor === 'object') {
                        this.groupTagsColor = {}
                        for (let key in data.groupTagsColor) {
                            let color = data.groupTagsColor[key]
                            this.groupTagsColor[key] = ref(common.fitterInputColor(color))
                        }
                    }
                }

                if (data.groupTagsTranslate !== null) {
                    this.groupTagsTranslate = data.groupTagsTranslate
                }

                if (data.blacklist !== null) {
                    this.blacklist = this._handleBlacklist(data.blacklist)
                }

                if (data.cancelBlacklistConfirm !== null) {
                    this.cancelBlacklistConfirm = data.cancelBlacklistConfirm
                }

                if (data.hotkey !== null) {
                    this.hotkey = data.hotkey
                }

                if (data.extraNetworksWidth !== null) {
                    this.extraNetworksWidth = data.extraNetworksWidth
                }

                if (data.extraNetworksHeight !== null) {
                    this.extraNetworksHeight = data.extraNetworksHeight
                }

                this.updateTranslateApiConfig()
                this.$refs.settingsModal.$refs.extensionCss.init()

                this.prompts.forEach(item => {
                    if (data[item.hideDefaultInputKey] !== null) {
                        item.hideDefaultInput = data[item.hideDefaultInputKey]
                    }
                    if (data[item.autoLoadWebuiPromptKey] !== null) {
                        item.autoLoadWebuiPrompt = data[item.autoLoadWebuiPromptKey]
                    }
                    if (data[item.hidePanelKey] !== null) {
                        item.hidePanel = data[item.hidePanelKey]
                    }
                    if (data[item.hideGroupTagsKey] !== null) {
                        item.hideGroupTags = data[item.hideGroupTagsKey]
                    }
                    item.$prompt = common.gradioApp().querySelector("#" + item.prompt)
                    item.$textarea = item.$prompt.getElementsByTagName("textarea")[0]
                    item.$steps = common.gradioApp().querySelector("#" + item.steps)
                })
                this.$nextTick(() => {
                    this.prompts.forEach(item => {
                        const $prompt = common.gradioApp().querySelector("#" + item.id)
                        console.log($prompt);
                        item.$prompt.parentElement.parentElement.after($prompt)
                        item.$prompt.parentElement.parentElement.style.display = item.hideDefaultInput ? 'none' : 'flex'
                        // item.$textarea.parentNode.appendChild($prompt)
                    })

                    this.startWatchSave = true
                })

                this.handlePaste()

                waitTick.addWaitTick(() => this.loadGroupTags())

                /*this.gradioAPI.getVersion().then(res => {
                    this.version = res.version
                    this.latestVersion = res.latest_version
                    this.isLatestVersion = res.version === res.latest_version
                })*/

                // todo: test
                // this.$refs.about.open()
                // this.$refs.chatgptPrompt.open()
                // this.$refs.promptFormat.open()
                // this.$refs.blacklist.open()
                // this.$refs.hotkey.open()
                // this.$refs.translateSetting.open(this.translateApi)
                /*this.$refs.extraNetworksPopup.show({
                    getBoundingClientRect: () => {
                        return {
                            top: 0,
                            left: 0,
                            width: 0,
                            height: 0,
                            bottom: 0,
                            right: 0,
                        }
                    },
                    offsetHeight: 26,
                }, 'FGOTiamatv2')*/
                /*this.onShowFavorite('phystonPrompt_txt2img_prompt', {
                    clientY: 150,
                    clientX: 283,
                })*/
            })
        },
        loadGroupTags() {
            return this.gradioAPI.getGroupTags(this.languageCode).then(data => {
                if (!data || data === '') {
                    this.groupTags = []
                } else {
                    try {
                        this.groupTags = jsYaml.load(data)
                        if (!Array.isArray(this.groupTags)) {
                            this.groupTags = []
                        }
                    } catch (e) {
                        console.log(e)
                        this.groupTags = []
                    }
                }
                this._handleGroupTags()
            })
        },
        _handleGroupTags() {
            let data = {toEn: new Map(), toLocal: new Map()}
            let setData = (en, local) => {
                const texts = [
                    en,
                    en.replace(/\_/g, ' '),
                    en.replace(/\-/g, ' '),
                ]
                texts.forEach((t) => {
                    if (data.toLocal.has(t)) {
                        let oldLocal = data.toLocal.get(t)
                        if (!oldLocal.includes(local)) {
                            oldLocal.push(local)
                        }
                    } else {
                        data.toLocal.set(t, [local])
                    }
                })
                data.toEn.set(local, en)
                // console.log('setData:groupTags', local, key, en)
            }
            this.groupTags.forEach((item, index) => {
                item.type = item.type || ''
                item.tabKey = 'groupTags-' + index
                item.groups.forEach((group, subIndex) => {
                    group.type = group.type || ''
                    group.tabKey = 'subGroupTags-' + index + '-' + subIndex
                    if (group.type == 'wrap') return
                    let key = common.getTagsColorKey(item.name, group.name)
                    if (!this.groupTagsColor[key]) {
                        this.groupTagsColor[key] = ref(common.fitterInputColor(group.color))
                    }
                    for (let en in group.tags) {
                        if (!en) continue
                        this.groupTagsColorKeyCache[en] = key

                        let local = group.tags[en]
                        if (!local || en == local) continue
                        setData(en, local)
                    }
                })
            })

            this.groupTagsTranslateCache = data
        },
        updateTippyState() {
            for (const $tippy of this.$tippyList) {
                if (this.enableTooltip) {
                    $tippy.enable()
                } else {
                    $tippy.disable()
                }
            }
        },
        updateTranslateApiConfig() {
            this.gradioAPI.getData('translate_api.' + this.translateApi).then(res => {
                let config = {}
                const apiItem = common.getTranslateApiItem(this.translateApis, this.translateApi)
                if (apiItem.config) {
                    for (const item of apiItem.config) {
                        if (apiItem.type === 'translators' && item.key === 'region' && !res['region']) {
                            config[item.key] = this.languageCode === 'zh_CN' || this.languageCode === 'zh_HK' || this.languageCode === 'zh_TW' ? 'China' : 'EN'
                        } else {
                            if (res) {
                                config[item.key] = res[item.key]
                            } else {
                                config[item.key] = item.default || ''
                            }
                        }
                    }
                    config['concurrent'] = apiItem.concurrent || 0
                }
                this.translateApiConfig = config
            })
        },
        onOpenSettings() {
            this.settingsVisible = true
        },
        onSelectLanguageClick(e) {
            this.$refs.selectLanguage.open(e)
        },
        handlePaste() {
            if (typeof gradioApp !== 'function') return
            const $pastes = gradioApp().querySelectorAll("#paste")
            if (!$pastes || $pastes.length <= 0) return
            $pastes.forEach(($paste, index) => {
                // 拷贝一个新的按钮
                const $pasteNew = $paste.cloneNode(true)
                $pasteNew.id = 'paste-new-' + index
                $pasteNew.innerHTML = '🗒'
                // 加到原来的按钮后面一个
                $paste.parentNode.insertBefore($pasteNew, $paste.nextSibling)
                // 原来的按钮隐藏
                // $paste.style.display = 'none'
                // 监听新按钮点击事件
                $pasteNew.addEventListener('click', () => {
                    this.pasteBtn = $paste
                    this.openPastePopup()
                })
                this.pasteTitle = $paste.title
            });
        },
        openPastePopup() {
            this.pasteContent = ''
            this.pasteLoading = false
            this.showPastePopup = true
        },
        closePastePopup() {
            this.showPastePopup = false
        },
        onClickPasteSubmit() {
            this.pasteLoading = true
            const ele = get_uiCurrentTabContent()
            let $textarea = null
            let $textareaNeg = null
            let $prompt = null
            let $promptNeg = null
            let ids = []
            for (const item of this.prompts) {
                if (item.tab == ele.id) {
                    console.log(item)
                    ids.push(item.id)
                    if (item.neg) {
                        $textareaNeg = item.$textarea
                        $promptNeg = item.$prompt
                    } else {
                        $textarea = item.$textarea
                        $prompt = item.$prompt
                    }
                }
            }
            if (!$textarea || !$prompt || !$promptNeg) {
                this.pasteLoading = false
                return
            }
            $textarea.value = this.pasteContent
            $textarea.dispatchEvent(new Event('input'))
            this.pasteBtn.dispatchEvent(new Event('click'))

            setTimeout(() => {
                let interval = 0
                let intervalI = 0
                interval = setInterval(() => {
                    intervalI++
                    if (intervalI > 100) {
                        this.pasteLoading = false
                        clearInterval(interval)
                        return
                    }
                    if ($prompt.getElementsByClassName('hide').length > 0 && $promptNeg.getElementsByClassName('hide').length > 0) {
                        this.pasteLoading = false
                        this.closePastePopup()
                        clearInterval(interval)
                        common.hideCompleteResults($textarea)
                        common.hideCompleteResults($textareaNeg)
                        ids.forEach((id, index) => {
                            setTimeout(() => {
                                this.$refs[id][0].onTextareaChange(true)
                            }, 1000)
                        })
                    }
                }, 100)
            }, 1000)
        },
        onUpdateHideDefaultInput(id, value) {
            const item = this.prompts.find(item => item.id == id)
            if (!item) return
            item.hideDefaultInput = value
            this.gradioAPI.setData(item.hideDefaultInputKey, item.hideDefaultInput)
            item.$prompt.parentElement.parentElement.style.display = item.hideDefaultInput ? 'none' : 'flex'
        },
        onUpdateAutoLoadWebuiPrompt(id, value) {
            const item = this.prompts.find(item => item.id == id)
            if (!item) return
            item.autoLoadWebuiPrompt = value
            this.gradioAPI.setData(item.autoLoadWebuiPromptKey, item.autoLoadWebuiPrompt)
        },
        onUpdateHidePanel(id, value) {
            const item = this.prompts.find(item => item.id == id)
            if (!item) return
            item.hidePanel = value
            this.gradioAPI.setData(item.hidePanelKey, item.hidePanel)
        },
        onUpdateHideGroupTags(id, value) {
            const item = this.prompts.find(item => item.id == id)
            if (!item) return
            item.hideGroupTags = value
            this.gradioAPI.setData(item.hideGroupTagsKey, item.hideGroupTags)
        },
        onShowHistory(id, e) {
            this.$refs.favorite.hide()
            this.historyCurrentPrompt = id
            const item = this.prompts.find(item => item.id == id)
            if (!item) return
            this.$refs.history.show(item.historyKey, e)
        },
        onUseHistory(history) {
            if (!this.historyCurrentPrompt) return
            const item = this.prompts.find(item => item.id == this.historyCurrentPrompt)
            if (!item) return
            this.$refs[item.id][0].useFavorite(history)
        },
        onShowFavorite(id, e) {
            this.$refs.history.hide()
            this.favoriteCurrentPrompt = id
            const item = this.prompts.find(item => item.id == id)
            if (!item) return
            this.$refs.favorite.show(item.favoriteKey, e)
        },
        onUseFavorite(favorite) {
            if (!this.favoriteCurrentPrompt) return
            const item = this.prompts.find(item => item.id == this.favoriteCurrentPrompt)
            if (!item) return
            this.$refs[item.id][0].useFavorite(favorite)
        },
        onRefreshFavorites(key) {
            this.$refs.favorite.getFavorites(key)
        },
        onShowChatgpt(id, e) {
            this.chatgptCurrentPrompt = id
            const item = this.prompts.find(item => item.id == id)
            if (!item) return
            this.$refs.chatgptPrompt.open()
        },
        onUseChatgpt(prompt) {
            if (!this.chatgptCurrentPrompt) return
            const item = this.prompts.find(item => item.id == this.chatgptCurrentPrompt)
            if (!item) return
            this.$refs[item.id][0].useChatgpt(prompt)
        },
        onSwitchTheme(newTheme) {
            this.theme = newTheme
            let currentUrl = window.location.href
            let url = new URL(currentUrl)
            let params = new URLSearchParams(url.search)
            if (params.has('__theme')) {
                params.set('__theme', this.theme);
            } else {
                params.append('__theme', this.theme);
            }
            let newUrl = url.origin + url.pathname + '?' + params.toString()
            window.location.href = newUrl
        },
        _handleBlacklist(blacklist) {
            blacklist = {...blacklist}
            blacklist.prompt = blacklist.prompt?.slice().map(item => item.toLowerCase())
            blacklist.negative_prompt = blacklist.negative_prompt?.slice().map(item => item.toLowerCase())
            blacklist.lora = blacklist.lora?.slice().map(item => item.toLowerCase())
            blacklist.lycoris = blacklist.lycoris?.slice().map(item => item.toLowerCase())
            blacklist.embedding = blacklist.embedding?.slice().map(item => item.toLowerCase())
            blacklist.translate = blacklist.translate?.slice().map(item => item.toLowerCase())
            return blacklist
        },
        onUpdateBlacklist(data, cancelBlacklistConfirm) {
            this.blacklist = this._handleBlacklist(data)
            if (typeof cancelBlacklistConfirm === "boolean") this.cancelBlacklistConfirm = cancelBlacklistConfirm
        },
        onUpdateHotkey(data) {
            this.hotkey = data
        },
        onUpdatePromptOption(id, field, value) {
            // 设置弹窗内按提示词框修改「自动加载WebUI提示词变动 / 隐藏默认输入框」
            // （这两个开关原先在主界面工具栏上，现值仍按提示词框各自独立存放）
            if (field === 'hideDefaultInput') {
                this.onUpdateHideDefaultInput(id, value)
            } else if (field === 'autoLoadWebuiPrompt') {
                this.onUpdateAutoLoadWebuiPrompt(id, value)
            }
        },
        onShowExtraNetworks(e, name, useCallback, showCheckpoints, from) {
            this.$refs.extraNetworksPopup.show(e, name, useCallback, showCheckpoints, from)
        },
        onHideExtraNetworks() {
            this.$refs.extraNetworksPopup.hide()
        },
        onRefreshExtraNetworks() {
            this._loadExtraNetworks()
        },
    },
}
</script>
