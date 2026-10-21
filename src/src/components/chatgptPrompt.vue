<template>
    <Transition name="fade">
        <!-- 改为「插件设置」同款模态：固定遮罩 + 居中弹窗 + 标题栏关闭按钮（2026-10-21 @TraeCode） -->
        <div class="physton-chatgpt-prompt" v-if="isOpen" @click="close">
        <div class="chatgpt-main paio-modal-main" @click.stop>
            <div class="paio-modal-header">
                <div class="paio-modal-title">{{ getLang('chatgpt_modal_title') }}</div>
                <div class="settings-modal-icon-btn" role="button" tabindex="0"
                     :aria-label="getLang('close')" :title="getLang('close')"
                     @click="close" @keydown.enter="close" @keydown.space.prevent="close">
                    <icon-svg name="close"/>
                </div>
            </div>
            <div class="chatgpt-body" @click.stop>
                <div :class="['body-panel', hidePanels['api'] ? 'fold': '']">
                    <div class="panel-header">
                        <div class="panel-unfold" @click="onUnfoldClick('api')">
                            <icon-svg class="hover-scale-120" name="unfold"/>
                        </div>
                        <div class="panel-title">{{ getLang('api_config') }}</div>
                    </div>
                    <div class="panel-content">
                        <div class="body-line" v-for="config in configs">
                            <div class="line-title">{{ configLabel(config) }}</div>
                            <div class="line-content">
                                <input type="text" v-if="config.type == 'input'"
                                       v-model="config.value" :placeholder="configPlaceholder(config)">
                                <select v-if="config.type == 'select'" v-model="config.value">
                                    <option v-for="option in config.options" :value="option">{{ option }}</option>
                                </select>
                                <div v-if="config.desc" v-html="config.desc"></div>
                            </div>
                        </div>
                        <div class="body-line">
                            <div class="line-title"></div>
                            <div class="line-content text-right">
                                <div class="common-btn hover-scale-120" @click="onSaveConfigClick">
                                    <icon-svg v-if="saveConfigIng" name="loading"/>
                                    <template v-else>{{ getLang('save') }}</template>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div :class="['body-panel', hidePanels['send'] ? 'fold': '']">
                    <div class="panel-header">
                        <div class="panel-unfold" @click="onUnfoldClick('send')">
                            <icon-svg class="hover-scale-120" name="unfold"/>
                        </div>
                        <div class="panel-title">{{ getLang('image_desc') }}</div>
                    </div>
                    <div class="panel-content">
                        <div class="body-line">
                            <div class="line-title">{{ getLang('preset') }}
                                <div class="line-subtitle">{{ getLang('ai_one') }}</div>
                            </div>
                            <div class="line-content">
                                <textarea :value="chatPreset" @change="onPresetChange" style="height: 100px"></textarea>
                            </div>
                        </div>
                        <div class="body-line">
                            <div class="line-title"></div>
                            <div class="line-content text-right">
                                <a href="javascript:" @click="onRestoreClick">{{ getLang('restore_to_default') }}</a>
                            </div>
                        </div>
                        <div class="body-line">
                            <div class="line-title">{{ getLang('image_desc') }}
                                <div class="line-subtitle">{{ getLang('ai_two') }}</div>
                            </div>
                            <div class="line-content">
                                <textarea style="height: 100px" ref="imageDesc" v-model="imageDesc"
                                          :placeholder="getLang('input_image_desc')"></textarea>
                            </div>
                        </div>
                        <div class="body-line">
                            <div class="line-title">{{ getLang('gen_source_title') }}</div>
                            <div class="line-content">
                                <div class="paio-gen-source" role="radiogroup" :aria-label="getLang('gen_source_title')">
                                    <label class="paio-gen-source-item">
                                        <input type="radio" value="local" v-model="genSource">
                                        <span>{{ localModelLabel }}</span>
                                    </label>
                                    <label class="paio-gen-source-item">
                                        <input type="radio" value="api" v-model="genSource">
                                        <span>{{ apiModelLabel }}</span>
                                    </label>
                                </div>
                            </div>
                        </div>
                        <div class="body-line">
                            <div class="line-title"></div>
                            <div class="line-content text-right">
                                <div class="common-btn hover-scale-120" @click="onGenClick">
                                    <icon-svg v-if="genIng" name="loading"/>
                                    <template v-else>{{ getLang('generate') }}</template>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div :class="['body-panel', hidePanels['result'] ? 'fold': '']">
                    <div class="panel-header">
                        <div class="panel-unfold" @click="onUnfoldClick('result')">
                            <icon-svg class="hover-scale-120" name="unfold"/>
                        </div>
                        <div class="panel-title">{{ getLang('generate_result') }}</div>
                    </div>
                    <div class="panel-content">
                        <div class="body-line">
                            <div class="line-title">{{ getLang('generate_result') }}</div>
                            <div class="line-content">
                                <textarea style="height: 100px" v-model="promptResult"></textarea>
                            </div>
                        </div>
                        <div class="body-line" v-if="promptResult">
                            <div class="line-title"></div>
                            <div class="line-content text-right">
                                <div class="common-btn hover-scale-120" @click="onUseClick">{{ getLang('use') }}</div>
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
import IconSvg from "@/components/iconSvg.vue";
import common from "@/utils/common";

export default {
    name: 'ChatgptPrompt',
    components: {IconSvg},
    mixins: [LanguageMixin],
    props: {},
    data() {
        return {
            isOpen: false,
            api: {},
            configs: [],
            chatPreset: '',
            hidePanels: {
                api: true,
            },
            imageDesc: '',
            promptResult: '',
            saveConfigIng: false,
            genIng: false,
            // 生成来源：local = models\LLM 里的本地模型；api = 上方 API 配置
            genSource: 'api',
            localModel: '',
        }
    },
    emits: ['use'],
    computed: {
        // 选项 1：本地模型名（models\LLM 里的模型，与翻译共用）
        localModelLabel() {
            return this.localModel || this.getLang('no_local_model')
        },
        // 选项 2：API 配置里的「模型名称」，没填则回落到「模型id」
        apiModelLabel() {
            let name = ''
            let modelId = ''
            this.configs.forEach(item => {
                if (item.key === 'model_name') name = (item.value || '').trim()
                if (item.key === 'model') modelId = (item.value || '').trim()
            })
            return name || modelId || this.getLang('unnamed_model')
        },
    },
    mounted() {
    },
    beforeUnmount() {
        this.setScrollLock(false)
    },
    methods: {
        // API 地址 / 模型 id 两行的标题改用中文可读文案（其余参数保持接口原英文名）
        configLabel(config) {
            if (config.key === 'api_base') return this.getLang('api_base_title')
            if (config.key === 'model') return this.getLang('model_title')
            if (config.key === 'model_name') return this.getLang('model_name_title')
            return config.title
        },
        configPlaceholder(config) {
            if (config.key === 'api_base') return this.getLang('api_base_placeholder')
            if (config.key === 'api_key') return this.getLang('api_key_placeholder')
            return ''
        },
        open() {
            this.isOpen = true
            this.setScrollLock(true)
            this.saveConfigIng = false
            this.genIng = false
            this.loadLocalModel()

            this.gradioAPI.getDatas(['chatgpt_prompts_preset', 'chatgpt_key', 'translate_api.openai']).then(res => {
                console.log(res)
                if (res.chatgpt_prompts_preset !== null) {
                    this.chatPreset = res.chatgpt_prompts_preset
                } else {
                    this.chatPreset = this.getLang('chatgpt_prompts_preset')
                }

                this.configs = []
                let configs = {}
                let api = common.getTranslateApiItem(this.translateApis, 'openai')
                api = JSON.parse(JSON.stringify(api))
                if (res.chatgpt_key && typeof res.chatgpt_key === 'object') {
                    for (const item of api.config) {
                        configs[item.key] = res.chatgpt_key[item.key] || item.default || ''
                    }
                } else {
                    /*if (res['translate_api.openai'] && res['translate_api.openai'].api_key) {
                        for (const item of api.config) {
                            configs[item.key] = res['translate_api.openai'][item.key] || item.default || ''
                        }
                    } else {*/
                    for (const item of api.config) {
                        configs[item.key] = item.default || ''
                    }
                    /*}*/
                    // this.gradioAPI.setData('chatgpt_key', configs)
                }
                if (!configs['api_key']) {
                    this.hidePanels['api'] = false
                }
                for (const item of api.config) {
                    item.value = configs[item.key]
                    this.configs.push(item)
                }
                // 【模型名称】：只属于本弹窗（存 chatgpt_key），不写进 translate_apis.json，
                // 免得翻译设置页的 OpenAI 接口参数里多出一栏。用于下方「生成方式」选项名。
                const nameIndex = this.configs.findIndex(item => item.key === 'model')
                this.configs.splice(nameIndex + 1, 0, {
                    key: 'model_name',
                    title: 'Model Name',
                    type: 'input',
                    value: (res.chatgpt_key && res.chatgpt_key['model_name']) || '',
                })
            })
        },
        close() {
            this.isOpen = false
            this.setScrollLock(false)
        },
        setScrollLock(lock) {
            // 弹窗打开时禁止背景页面滚轮滚动（与「插件设置」弹窗一致）
            const cls = 'paio-scroll-locked'
            if (lock) {
                const sw = window.innerWidth - document.documentElement.clientWidth
                document.body.style.paddingRight = sw > 0 ? sw + 'px' : ''
            } else {
                document.body.style.paddingRight = ''
            }
            const targets = [
                document.documentElement,
                document.body,
                ...document.getElementsByTagName('gradio-app'),
                ...document.querySelectorAll('.gradio-container'),
            ]
            targets.forEach(el => el && el.classList.toggle(cls, lock))
        },
        onUnfoldClick(panelName) {
            this.hidePanels[panelName] = !this.hidePanels[panelName]
        },
        onSaveConfigClick() {
            if (this.saveConfigIng) return
            this.saveConfigIng = true
            let configs = {}
            this.configs.forEach(item => {
                configs[item.key] = item.value
            })
            this.gradioAPI.setData('chatgpt_key', configs).then(res => {
                this.$toastr.success(this.getLang('success'))
                this.saveConfigIng = false
            }).catch(err => {
                this.$toastr.error(err.message || err)
                this.saveConfigIng = false
            })
        },
        onPresetChange(e) {
            this.chatPreset = e.target.value
            this._saveChatPreset()
        },
        onRestoreClick() {
            this.chatPreset = this.getLang('chatgpt_prompts_preset')
            this._saveChatPreset()
        },
        _saveChatPreset() {
            this.gradioAPI.setData('chatgpt_prompts_preset', this.chatPreset)
        },
        onGenClick() {
            if (this.genIng) return
            if (!this.imageDesc) return this.$refs.imageDesc.focus()
            this.imageDesc = this.imageDesc.trim()
            if (!this.imageDesc) return this.$refs.imageDesc.focus()
            this.genIng = true
            let messages = [
                {'role': 'user', 'content': this.chatPreset},
                {'role': 'user', 'content': this.imageDesc},
            ]
            let configs = {}
            this.configs.forEach(item => {
                configs[item.key] = item.value
            })
            const request = this.genSource === 'local'
                ? this.gradioAPI.localLLMGen(messages)
                : this.gradioAPI.genOpenAI(messages, configs)
            request.then(res => {
                if (res.success) {
                    this.promptResult = res.result
                } else {
                    this.$toastr.error(res.message || 'error')
                }
                this.genIng = false
            }).catch(err => {
                this.$toastr.error(err.message || err)
                this.genIng = false
            })
        },
        // 读取 models\LLM 里当前选中的本地模型名（与【本地AI大模型翻译】共用同一模型）
        loadLocalModel() {
            this.gradioAPI.localLLMStatus().then(res => {
                if (res && res.ok) {
                    this.localModel = res.model || res.selected || ''
                }
            }).catch(() => {
                this.localModel = ''
            })
        },
        onUseClick() {
            this.$emit('use', this.promptResult)
            this.close()
        },
    },
}
</script>