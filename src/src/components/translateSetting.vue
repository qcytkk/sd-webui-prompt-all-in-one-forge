<template>
    <Transition name="fadeDown">
        <div :class="['physton-prompt-translate-setting', {'embedded-host': embedded}]" v-if="isOpen" @click="onCloseClick">
            <div class="translate-setting-main" @click.stop>
                <div class="translate-setting-close" v-if="!embedded" @click="onCloseClick">
                    <icon-svg name="close"/>
                </div>
                <div class="translate-setting-content" @click.stop>
                    <!-- ① 翻译接口（分组标题沿用 translate_api，原行内重复标题已去掉） -->
                    <div class="settings-section">
                        <div class="settings-section-title" role="heading" aria-level="3">{{ getLang('translate_api') }}</div>
                        <div class="setting-line">
                            <div class="line-text"></div>
                            <div class="line-content">
                                <select :aria-label="getLang('translate_api')" v-model="apiKey">
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
                                <div class="line-title">{{ config.title }}</div>
                            </div>
                            <div class="line-content">
                                <input type="text" v-if="config.type == 'input'" v-model="config.value" @change="onChangeConfigValue(config)">
                                <select v-if="config.type == 'select'" v-model="config.value">
                                    <option v-for="option in config.options" :value="option">{{ option }}</option>
                                </select>
                                <div v-if="config.desc" v-html="config.desc"></div>
                            </div>
                        </div>
                    </div>
                    <!-- ② 翻译测试 -->
                    <div class="settings-section">
                        <div class="settings-section-title" role="heading" aria-level="3">{{ getLang('translate_test') }}</div>
                        <div class="setting-line">
                            <div class="line-text"></div>
                            <div class="line-content">
                                <textarea class="test-input" :aria-label="getLang('translate_test')" v-model="testText"></textarea>
                            </div>
                        </div>
                        <div class="setting-line">
                            <div class="line-text"></div>
                            <div class="line-content">
                                <div class="hover-scale-120 test-btn" @click="onTestClick">
                                    <icon-svg v-if="loading" name="loading"/>
                                    <template v-else>{{getLang('test')}}</template>
                                </div>
                            </div>
                        </div>
                        <div class="setting-line">
                            <div class="line-text"></div>
                            <div class="line-content">
                                <div class="translate-error" v-if="!translateSuccess && errorMessage">{{ errorMessage }}</div>
                                <textarea class="test-input" v-if="translatedText" v-model="translatedText"></textarea>
                            </div>
                        </div>
                    </div>
                    <!-- ③ 翻译增强（关键词组 + TagComplete） -->
                    <div class="settings-section">
                        <div class="settings-section-title" role="heading" aria-level="3">{{ getLang('enhance_translation') }}</div>
                        <!-- 关键词组与 CSV 词典是 if / else-if 互斥关系（见 phystonPrompt.vue 的翻译分支），
                             这里直接告诉用户当前实际生效的是哪一个，避免"改了没反应"的困惑 -->
                        <div class="setting-line">
                            <div class="line-text">
                                <div class="line-title">{{ getLang('translation_source') }}</div>
                            </div>
                            <div class="line-content">
                                <span class="paio-source-badge" :class="{'is-off': translationSource === 'none'}">{{ translationSourceText }}</span>
                            </div>
                        </div>
                        <div class="setting-line">
                            <div class="line-text">
                                <div class="line-title">{{ getLang('Keyword_group') }}</div>
                            </div>
                            <div class="line-content">
                                <div v-html="getLang('enhance_translation_use_Keyword_group_desc')"></div>
                                <label class="onlyCsvOnAuto">
                                    <input class="hover-scale-120" type="checkbox" value="1" v-model="groupTagsTranslateValue">
                                    <span>{{ getLang('enhance_translation_use_keyword_group') }}</span>
                                </label>
                            </div>
                        </div>
                        <div class="setting-line">
                            <div class="line-text">
                                <div class="line-title">TagComplete</div>
                            </div>
                            <div class="line-content">
                                <div v-html="getLang('tagcomplete_translate_desc')"></div>
                                <div class="common-red" v-html="getLang('tagcomplete_translate_desc2')"></div>
                                <div class="line-row">
                                    <select v-model="tagCompleteFileKey" @change="tagCompleteResults = []">
                                        <option v-for="item in tagCompleteFiles" :value="item.key">{{ item.name }}</option>
                                    </select>
                                    <div class="refresh-btn hover-scale-120" v-tooltip="getLang('refresh')" @click="refreshCSVs">
                                        <icon-svg v-if="tagCompleteFilesLoading" name="loading"/>
                                        <icon-svg v-else name="refresh" />
                                    </div>
                                </div>
                                <label class="onlyCsvOnAuto" :style="{display: tagCompleteFileKey ? 'flex': 'none'}">
                                    <input class="hover-scale-120" type="checkbox" value="1" v-model="onlyCsvOnAutoValue">
                                    <span>{{ getLang('only_csv_on_auto') }}</span>
                                </label>
                            </div>
                        </div>
                        <div class="setting-line" v-show="tagCompleteFileKey">
                            <div class="line-text"></div>
                            <div class="line-content">
                                <div class="hover-scale-120 test-btn" @click="onTagCompleteTestClick">{{ getLang('test') }}</div>
                                <div ref="tagCompleteResults" v-show="tagCompleteResults.length > 0">
                                    <p v-for="text in tagCompleteResults" :key="text">{{ text }}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="setting-btns">
                        <div class="translate-save hover-scale-120" @click="onSaveClick">{{ getLang('save') }}</div>
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
        // 与 phystonPrompt.vue 的翻译分支保持一致：关键词组优先，其次 CSV 词典，都没有则全部走网络
        translationSource() {
            if (this.groupTagsTranslateValue) return 'group_tags'
            if (this.tagCompleteFileKey) return 'csv'
            return 'none'
        },
        translationSourceText() {
            if (this.translationSource === 'group_tags') return this.getLang('Keyword_group')
            if (this.translationSource === 'csv') return this.getLang('source_csv_dict')
            return this.getLang('source_network_only')
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
        onChangeConfigValue(config) {
            if (config.type === 'input' && config.value === '' && config.default) {
                config.value = config.default
            }
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
        onSaveClick() {
            let configs = {}
            for (const item of this.configs) {
                configs[item.key] = item.value
            }
            this.$emit('update:translateApi', this.apiKey)
            this.$emit('update:tagCompleteFile', this.tagCompleteFileKey)
            this.$emit('update:onlyCsvOnAuto', this.onlyCsvOnAutoValue)
            this.$emit('update:groupTagsTranslate', this.groupTagsTranslateValue)
            this.gradioAPI.setData('translate_api.' + this.apiKey, configs).then(res => {
                if (this.apiKey === this.translateApi) this.$emit('forceUpdate:translateApi')
            })
            // 嵌入设置弹窗后不再「保存即关闭」——旧的弹窗行为会让本页内容消失，这里只给个轻提示
            this.$toastr.success(this.getLang('success'))
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
