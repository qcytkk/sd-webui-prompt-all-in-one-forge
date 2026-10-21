<template>
    <div :class="['physton-prompt-extension-css', {'embedded-host': embedded}]" v-if="isOpen" @click="close">
        <div class="extension-main" @click.stop>
            <div class="extension-close" v-if="!embedded" @click="close">
                <icon-svg name="close"/>
            </div>
            <div class="extension-list" @click.stop>
                <!-- 按 manifest.type 分类（theme 主题 / enhance 增强），分组标题用小标题 + 组内虚线分隔 -->
                <div class="settings-section" v-for="group in groupedList" :key="group.type">
                    <div class="settings-section-title" role="heading" aria-level="3">{{ getLang(group.type) }}</div>
                    <div class="setting-line" v-for="item in group.items" :key="item.dir">
                        <div class="line-text">
                            <div class="line-title">{{ getName(item) }}</div>
                            <div class="line-desc">{{ getItemInfo(item) }}</div>
                        </div>
                        <div class="line-content">
                            <input type="checkbox" :checked="item.selected"
                                   :aria-label="getName(item)"
                                   @change="onChangeSelect(item.id)">
                        </div>
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
    name: 'ExtensionCss',
    components: {IconSvg},
    mixins: [LanguageMixin],
    props: {
        embedded: {type: Boolean, default: false},
    },
    data() {
        return {
            isOpen: false,
            list: [],
        }
    },
    computed: {
        // list 已按 type + dir 排好序，这里只做分组（分组顺序随首次出现的 type）
        groupedList() {
            const groups = []
            this.list.forEach(item => {
                const type = item.manifest.type || 'enhance'
                let group = groups.find(g => g.type === type)
                if (!group) {
                    group = {type, items: []}
                    groups.push(group)
                }
                group.items.push(item)
            })
            return groups
        },
    },
    mounted() {
    },
    methods: {
        init() {
            this.refresh(true)
        },
        refresh(init = false) {
            this.gradioAPI.getExtensionCssList().then(res => {
                let list = []
                for (let i = 0; i < res.length; i++) {
                    res[i].manifest = JSON.parse(res[i].manifest)
                    if (!res[i].manifest) continue
                    if (typeof res[i].manifest !== 'object') continue
                    if (!res[i].manifest.name) continue
                    res[i].selected = res[i].selected || false
                    res[i].id = 'physton-prompt-extension-' + res[i].dir
                    list.push(res[i])
                }

                list.forEach(item => {
                    item.sort = item.manifest.type + '.' + item.dir
                })
                list.sort((a, b) => {
                    return a.sort > b.sort ? 1 : -1
                })

                this.list = list
                if (init) {
                    this.list.forEach(item => {
                        if (item.selected) {
                            common.loadCSS(item.style, item.id, true, false)
                        }
                    })
                }
            })
        },
        getName(item) {
            if (!item) return ''
            let name = item.manifest.name
            if (item.manifest.i18n && item.manifest.i18n[this.languageCode]) {
                name = item.manifest.i18n[this.languageCode]
            }
            return name
        },
        getItemInfo(item) {
            let parts = []
            if (item.dir) parts.push(item.dir)
            if (item.manifest.author) parts.push('By: ' + item.manifest.author)
            return parts.join(' · ')
        },
        onChangeSelect(id) {
            let item = this.list.find(item => item.id === id)
            if (!item) return
            item.selected = !item.selected
            if (item.selected) {
                common.loadCSS(item.style, item.id, true, false)
            } else {
                common.removeCSS(item.id)
            }
            this.gradioAPI.setData(item.dataName, item.selected)
        },
        open() {
            this.isOpen = true
            this.refresh(false)
        },
        close() {
            this.isOpen = false
        }
    },
}
</script>