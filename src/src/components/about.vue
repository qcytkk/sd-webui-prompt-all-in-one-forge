<template>
    <div :class="['physton-about-prompt', {'embedded-host': embedded}]" v-if="isOpen" @click="close">
        <div class="about-main" @click.stop>
            <div class="about-close" v-if="!embedded" @click="close">
                <icon-svg name="close"/>
            </div>
            <div class="about-body" @click.stop>
                <p class="body-title">{{ globals.name }}</p>
                <p v-if="!loading">
                    <span>{{ getLang('version') }}: {{ formatVersion(version) }}</span>
                </p>
                <!-- 插件来源与联动说明（2026-10-21 @TraeCode） -->
                <div class="about-links">
                    <div class="about-link-item">
                        <div class="about-link-title">{{ getLang('about_original_plugin') }}</div>
                        <a class="about-link" href="https://github.com/Physton/sd-webui-prompt-all-in-one"
                           target="_blank" rel="noopener noreferrer">https://github.com/Physton/sd-webui-prompt-all-in-one</a>
                    </div>
                    <div class="about-link-item">
                        <div class="about-link-title">{{ getLang('about_this_plugin') }}</div>
                        <a class="about-link" href="https://github.com/qcytkk/sd-webui-prompt-all-in-one-forge"
                           target="_blank" rel="noopener noreferrer">https://github.com/qcytkk/sd-webui-prompt-all-in-one-forge</a>
                        <div class="about-link-desc">{{ getLang('about_this_plugin_desc') }}</div>
                    </div>
                    <div class="about-link-item">
                        <div class="about-link-title">{{ getLang('about_linked_plugin') }}</div>
                        <a class="about-link" href="https://github.com/qcytkk/sd_forge_lora_new"
                           target="_blank" rel="noopener noreferrer">https://github.com/qcytkk/sd_forge_lora_new</a>
                        <div class="about-link-desc">{{ getLang('about_linked_plugin_desc') }}</div>
                    </div>
                    <div class="about-link-item">
                        <div class="about-link-title">{{ getLang('about_features') }}</div>
                        <div class="about-link-desc">{{ getLang('about_features_desc') }}</div>
                    </div>
                </div>
                <div class="version-list">
                    <icon-svg v-if="loading" name="loading"/>
                    <div class="version-item" v-for="(item) in versions" :key="item.version">
                        <div class="item-header">
                            <div class="version-sha">{{ formatVersion(item.version) }}</div>
                            <div class="version-date">{{ item.date }}</div>
                        </div>
                        <div class="version-msg" v-html="message(item.message)"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
import LanguageMixin from "@/mixins/languageMixin";
import IconSvg from "@/components/iconSvg.vue";
import common from "@/utils/common";

export default {
    name: 'About',
    components: {IconSvg},
    mixins: [LanguageMixin],
    props: {
        embedded: {type: Boolean, default: false},
    },
    data() {
        return {
            version: '',
            latestVersion: '',
            isLatestVersion: true,

            isOpen: false,
            loading: false,
            versions: [],
        }
    },
    emits: ['use'],
    computed: {},
    methods: {
        open() {
            this.isOpen = true
            this.version = ''
            this.latestVersion = ''
            this.isLatestVersion = true
            this.versions = []
            this.loading = true
            this.gradioAPI.getVersion().then(res => {
                this.version = res.version
                this.latestVersion = res.latest_version
                this.isLatestVersion = res.version === res.latest_version
            })
            this.gradioAPI.getRemoteVersions().then(res => {
                this.loading = false
                let versions = []
                res.forEach((item, index) => {
                    if (item.is_update_readme) return
                    item.date = common.formatTime(item.date)
                    versions.push(item)
                })
                this.versions = versions
            }).catch(err => {
                this.loading = false
            })
        },
        close() {
            this.isOpen = false
        },
        formatVersion(version) {
            if (!version) return this.getLang('unknown_version')
            // 语义版本号（如 0.1.0）原样显示；git commit 只取前 7 位
            if (/^\d+\.\d+/.test(version)) return version
            return version.slice(0, 7)
        },
        message(text) {
            text = common.escapeHtml(text)
            text = text.replace(/Former-commit-id: [a-z0-9]{40}/g, '')
            text = text.trim()
            text = text.replace("\n", '<br/>')
            return text
        },
    },
}
</script>
