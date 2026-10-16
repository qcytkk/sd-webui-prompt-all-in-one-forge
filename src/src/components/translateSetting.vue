<template>
    <Transition name="fadeDown">
        <div :class="['physton-prompt-translate-setting', {'embedded-host': embedded}]" v-if="isOpen" @click="onCloseClick">
            <div class="translate-setting-main" @click.stop>
                <div class="translate-setting-close" v-if="!embedded" @click="onCloseClick">
                    <icon-svg name="close"/>
                </div>
                <div class="translate-setting-content" @click.stop>
                    <!-- ① 翻译接口（分组标题沿用 translate_api，原行内重复标题已去掉）
                         本组各行（下拉 / 红字说明 / 帮助链接 / 各参数行）同属「配置当前翻译接口」一块，
                         加 .paio-plain 去掉组内虚线 -->
                    <div class="settings-section paio-plain">
                        <div class="settings-section-title" role="heading" aria-level="3">{{ getLang('translate_api') }}</div>
                        <div class="setting-line">
                            <div class="line-text"></div>
                            <div class="line-content">
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
                        <div class="setting-line" v-if="apiItem && apiItem.type == 'translators'">
                            <div class="line-text"></div>
                            <div class="line-content">
                                <span class="common-red">*{{ getLang('not_api_key_desc') }}</span>
                            </div>
                        </div>
                        <div class="setting-line" v-if="apiItem.help">
                            <div class="line-text"></div>
                            <div class="line-content">
                                <div v-for="item in apiItem.help" class="help-list">
                                    <div class="help-item">[?] <a :href="item.url" target="_blank">{{ item.title }}</a></div>
                                </div>
                            </div>
                        </div>
                        <div class="setting-line" v-for="config in configs">
                            <div class="line-text">
                                <div class="line-title">{{ configLabel(config) }}</div>
                            </div>
                            <div class="line-content">
                                <input type="text" v-if="config.type == 'input'" v-model="config.value" @change="onChangeConfigValue(config)">
                                <select v-if="config.type == 'select'" v-model="config.value" @change="onConfigSelectChange(config, $event)">
                                    <option v-for="option in config.options" :value="option">{{ option }}</option>
                                </select>
                                <div v-if="config.desc" v-html="config.desc"></div>
                            </div>
                        </div>
                    </div>
                    <!-- ② 翻译测试（输入框 / 测试按钮 / 结果 同属一个测试功能，加 .paio-plain 去掉组内虚线；
                         加 .paio-no-sep 去掉与上一组「翻译接口」之间的组间虚线） -->
                    <div class="settings-section paio-plain paio-no-sep">
                        <div class="settings-section-title" role="heading" aria-level="3">{{ getLang('translate_test') }}</div>
                        <!-- 第一行两栏：左=翻译原文，右=翻译结果 -->
                        <div class="setting-line paio-test-pair">
                            <div class="line-text"></div>
                            <div class="line-content">
                                <textarea class="test-input" :aria-label="getLang('translate_test')" v-model="testText"></textarea>
                                <textarea class="test-input" :aria-label="getLang('translate_result')" v-model="translatedText"></textarea>
                            </div>
                        </div>
                        <!-- 第二行：测试按钮（失败时在其左侧显示错误信息） -->
                        <div class="setting-line">
                            <div class="line-text"></div>
                            <div class="line-content">
                                <div class="translate-error" v-if="!translateSuccess && errorMessage">{{ errorMessage }}</div>
                                <div class="hover-scale-120 test-btn" @click="onTestClick">
                                    <icon-svg v-if="loading" name="loading"/>
                                    <template v-else>{{getLang('test')}}</template>
                                </div>
                            </div>
                        </div>
                    </div>
                    <!-- ③ 翻译增强（关键词组 + TagComplete） -->
                    <div class="settings-section">
                        <div class="settings-section-title" role="heading" aria-level="3">{{ getLang('enhance_translation') }}</div>
                        <!-- 翻译是「依次回退」的链：关键词组 → CSV 词典 → 网络
                             （见 phystonPrompt.vue 的 translateByGroupTags 会把未命中的词交给 translateByCSV），
                             这里把当前生效的档位按顺序显示出来，避免"改了没反应"的困惑 -->
                        <div class="setting-line">
                            <div class="line-text">
                                <div class="line-title">{{ getLang('translation_source') }}</div>
                            </div>
                            <div class="line-content">
                                <span class="paio-source-badge" :class="{'is-off': translationChainOff}">{{ translationChainText }}</span>
                            </div>
                        </div>
                        <!-- 说明 + 勾选框，同样纵向分 2 行（与下方 TagComplete 行保持一致） -->
                        <div class="setting-line paio-col">
                            <div class="line-text">
                                <div class="line-title">{{ getLang('Keyword_group') }}</div>
                            </div>
                            <div class="line-content">
                                <div v-html="getLang('enhance_translation_use_Keyword_group_desc')"></div>
                                <label class="onlyCsvOnAuto">
                                    <input class="hover-scale-120" type="checkbox" value="1"
                                           v-model="groupTagsTranslateValue" @change="onGroupTagsTranslateChange($event)">
                                    <span>{{ getLang('enhance_translation_use_keyword_group') }}</span>
                                </label>
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
                </div>
            </div>
        </div>
    </Transition>
</template>
<script>
import LanguageMixin from "@/mixins/languageMixin";
import common from "@/utils/common";
import IconSvg from "@/components/iconSvg.vue";

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
                // group.children = group.children.filter(item => item.support[this.languageCode])
                group.children.forEach(item => {
                    item.disabled = !item.support[this.languageCode]
                })
            })
            return api
        },
        // 翻译来源是「依次回退」的链，不是二选一：关键词组未命中 → CSV 词典未命中 → 网络
        // （与 phystonPrompt.vue 的 translateByGroupTags / translateByCSV 分支保持一致）
        translationChainOff() {
            return !this.groupTagsTranslateValue && !this.tagCompleteFileKey
        },
        translationChainText() {
            let parts = []
            if (this.groupTagsTranslateValue) parts.push(this.getLang('Keyword_group'))
            if (this.tagCompleteFileKey) parts.push(this.getLang('source_csv_dict'))
            parts.push(this.getLang('source_network'))
            return parts.join(' → ')
        },
    },
    mounted() {
        this.translateSuccess = false
        this.errorMessage = ''
        this.translatedText = ''
        this.loading = false
    },
    emits: ['update:translateApi', 'forceUpdate:translateApi', 'update:tagCompleteFile', 'update:onlyCsvOnAuto', 'update:groupTagsTranslate'],
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
        onCloseClick() {
            this.isOpen = false
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
    },
}
</script>
