<template>
    <!-- 【标签快捷列表】自定义分组：保存到 group_tags/append.yaml，追加在内置列表末尾 -->
    <div :class="['physton-prompt-group-tags', {'embedded-host': embedded}]" v-if="isOpen">
        <div class="settings-section">
            <div class="line-desc paio-gt-desc">{{ getLang('group_tags_page_desc') }}</div>

            <div class="paio-gt-category" v-for="(cat, ci) in categories" :key="'cat-' + ci">
                <div class="paio-gt-row">
                    <input type="text" class="paio-dict-input" v-model="cat.name"
                           :placeholder="getLang('group_tags_category_name')"
                           :aria-label="getLang('group_tags_category_name')">
                    <button type="button" class="paio-btn is-danger" @click="removeCategory(ci)">
                        <icon-svg name="remove"/>
                        <span>{{ getLang('dict_action_delete') }}</span>
                    </button>
                </div>

                <div class="paio-gt-group" v-for="(group, gi) in cat.groups" :key="'group-' + gi">
                    <div class="paio-gt-row">
                        <input type="text" class="paio-dict-input" v-model="group.name"
                               :placeholder="getLang('group_tags_group_name')"
                               :aria-label="getLang('group_tags_group_name')">
                        <input type="text" class="paio-dict-input paio-gt-color" v-model="group.color"
                               :placeholder="getLang('group_tags_group_color')"
                               :aria-label="getLang('group_tags_group_color')">
                        <button type="button" class="paio-btn is-danger" @click="removeGroup(cat, gi)">
                            <icon-svg name="remove"/>
                            <span>{{ getLang('dict_action_delete') }}</span>
                        </button>
                    </div>

                    <div class="paio-gt-tag-row" v-for="(tag, ti) in group.tags" :key="'tag-' + ti">
                        <input type="text" class="paio-dict-input" v-model="tag.en"
                               :placeholder="getLang('group_tags_tag_en')"
                               :aria-label="getLang('group_tags_tag_en')">
                        <span class="paio-gt-arrow">→</span>
                        <input type="text" class="paio-dict-input" v-model="tag.local"
                               :placeholder="getLang('group_tags_tag_local')"
                               :aria-label="getLang('group_tags_tag_local')">
                        <button type="button" class="paio-btn paio-gt-mini" @click="removeTag(group, ti)"
                                :aria-label="getLang('dict_action_delete')">
                            <icon-svg name="remove"/>
                        </button>
                    </div>

                    <button type="button" class="paio-btn" @click="addTag(group)">
                        <span>{{ getLang('group_tags_add_tag') }}</span>
                    </button>
                </div>

                <button type="button" class="paio-btn" @click="addGroup(cat)">
                    <span>{{ getLang('group_tags_add_group') }}</span>
                </button>
            </div>

            <div class="paio-gt-empty" v-if="!categories.length">{{ getLang('group_tags_empty') }}</div>

            <div class="paio-gt-footer">
                <button type="button" class="paio-btn" @click="addCategory">
                    <icon-svg name="favorite"/>
                    <span>{{ getLang('group_tags_add_category') }}</span>
                </button>
                <button type="button" class="paio-btn is-primary" :disabled="saving"
                        :aria-busy="saving ? 'true' : 'false'" @click="save">
                    <icon-svg v-if="saving" name="loading" class="is-spinning"/>
                    <span>{{ getLang('save') }}</span>
                </button>
            </div>
        </div>
        <!-- 删除二次确认：删除不可撤销，避免误操作 -->
        <div class="paio-dict-mask is-top" v-if="confirmVisible" @click.stop>
            <div class="paio-dict-dialog paio-dict-sub" role="dialog" aria-modal="true"
                 :aria-label="getLang('dict_action_delete')">
                <div class="paio-dict-header">
                    <div class="paio-dict-title">{{ getLang('dict_action_delete') }}</div>
                    <button type="button" class="paio-icon-btn" :aria-label="getLang('close')"
                            :title="getLang('close')" @click="cancelConfirm">
                        <icon-svg name="close"/>
                    </button>
                </div>
                <div class="paio-dict-body">
                    <p class="paio-dict-confirm">{{ confirmText }}</p>
                </div>
                <div class="paio-dict-footer">
                    <button type="button" class="paio-btn" @click="cancelConfirm">
                        <span>{{ getLang('close') }}</span>
                    </button>
                    <button type="button" class="paio-btn is-danger-solid" @click="confirmDelete">
                        <span>{{ getLang('dict_delete_confirm_btn') }}</span>
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import LanguageMixin from "@/mixins/languageMixin";
import IconSvg from "@/components/iconSvg.vue";
import common from "@/utils/common";
import jsYaml from "js-yaml";
import tinycolor from "tinycolor2";

export default {
    name: 'GroupTagsSetting',
    components: {IconSvg},
    mixins: [LanguageMixin],
    props: {
        embedded: {type: Boolean, default: false},
    },
    data() {
        return {
            isOpen: false,
            loading: false,
            saving: false,
            categories: [],
            // 删除二次确认
            confirmVisible: false,
            confirmText: '',
            confirmAction: null,
        }
    },
    methods: {
        open() {
            this.isOpen = true
            this.cancelConfirm()
            this.load()
        },
        close() {
            this.isOpen = false
            this.cancelConfirm()
        },
        load() {
            if (this.loading) return
            this.loading = true
            this.gradioAPI.getGroupTagsCustom().then(text => {
                this.loading = false
                this.categories = this.parse(text)
            }).catch(() => {
                this.loading = false
                this.categories = []
                this.$toastr.error(this.getLang('failed'))
            })
        },
        parse(text) {
            if (!text || !text.trim()) return []
            let data = null
            try {
                data = jsYaml.load(text)
            } catch (e) {
                this.$toastr.error(this.getLang('group_tags_parse_error'))
                return []
            }
            if (!Array.isArray(data)) return []
            return data.map(item => {
                const category = {name: (item && item.name) || '', groups: []}
                const groups = item && Array.isArray(item.groups) ? item.groups : []
                category.groups = groups.map(group => {
                    const out = {
                        name: (group && group.name) || '',
                        color: (group && group.color) || '',
                        tags: [],
                    }
                    const tags = group && group.tags
                    if (Array.isArray(tags)) {
                        tags.forEach(tag => {
                            if (tag && typeof tag === 'object' && !Array.isArray(tag)) {
                                for (const en in tag) {
                                    out.tags.push({en: String(en), local: tag[en] == null ? '' : String(tag[en])})
                                }
                            } else if (typeof tag === 'string') {
                                out.tags.push({en: tag, local: ''})
                            }
                        })
                    } else if (tags && typeof tags === 'object') {
                        for (const en in tags) {
                            out.tags.push({en: String(en), local: tags[en] == null ? '' : String(tags[en])})
                        }
                    }
                    return out
                })
                return category
            })
        },
        blankGroup() {
            return {name: '', color: '', tags: [{en: '', local: ''}]}
        },
        addCategory() {
            this.categories.push({name: '', groups: [this.blankGroup()]})
        },
        removeCategory(index) {
            const cat = this.categories[index] || {}
            const name = (cat.name || '').trim() || '-'
            const text = this.getLang('group_tags_delete_category_confirm').replace('{0}', name)
            this.askDelete(text, () => {
                this.categories.splice(index, 1)
            })
        },
        addGroup(cat) {
            cat.groups.push(this.blankGroup())
        },
        removeGroup(cat, index) {
            const group = cat.groups[index] || {}
            const name = (group.name || '').trim() || '-'
            const text = this.getLang('group_tags_delete_group_confirm').replace('{0}', name)
            this.askDelete(text, () => {
                cat.groups.splice(index, 1)
            })
        },
        addTag(group) {
            group.tags.push({en: '', local: ''})
        },
        removeTag(group, index) {
            const tag = group.tags[index] || {}
            let name = (tag.en || '').trim() || '-'
            if (name.length > 40) name = name.slice(0, 40) + '…'
            const text = this.getLang('group_tags_delete_tag_confirm').replace('{0}', name)
            this.askDelete(text, () => {
                group.tags.splice(index, 1)
            })
        },
        // ── 删除二次确认弹窗 ──
        askDelete(text, action) {
            this.confirmText = text
            this.confirmAction = action
            this.confirmVisible = true
        },
        cancelConfirm() {
            this.confirmVisible = false
            this.confirmAction = null
        },
        confirmDelete() {
            const action = this.confirmAction
            this.confirmVisible = false
            this.confirmAction = null
            if (typeof action === 'function') action()
        },
        buildList() {
            const list = []
            this.categories.forEach(cat => {
                const name = (cat.name || '').trim()
                if (!name) return
                const groups = []
                cat.groups.forEach(group => {
                    const tags = {}
                    group.tags.forEach(tag => {
                        const en = (tag.en || '').trim()
                        if (!en) return
                        tags[en] = (tag.local || '').trim()
                    })
                    const groupName = (group.name || '').trim()
                    if (!groupName || !Object.keys(tags).length) return
                    const out = {name: groupName, tags}
                    const color = (group.color || '').trim()
                    if (color) out.color = color
                    groups.push(out)
                })
                if (!groups.length) return
                list.push({name, groups})
            })
            return list
        },
        buildYaml() {
            const list = this.buildList()
            if (!list.length) return ''
            return jsYaml.dump(list, {lineWidth: -1, noRefs: true})
        },
        save() {
            if (this.saving) return
            const list = this.buildList()
            // 颜色写错时明确提示，避免被静默当成透明色
            for (const cat of list) {
                const bad = cat.groups.find(group => group.color && !tinycolor(group.color).isValid())
                if (bad) {
                    this.$toastr.error(this.getLang('group_tags_invalid_color').replace('{0}', bad.color))
                    return
                }
            }
            this.saving = true
            const content = this.buildYaml()
            this.gradioAPI.saveGroupTagsCustom(content).then(res => {
                this.saving = false
                if (!res || !res.success) {
                    this.$toastr.error((res && res.message) || this.getLang('failed'))
                    return
                }
                this.$toastr.success(this.getLang('success'))
                // 颜色已持久化在主界面缓存里，仅刷新 YAML 不会覆盖旧色，这里显式同步
                const colors = []
                list.forEach(cat => {
                    cat.groups.forEach(group => {
                        colors.push({
                            key: common.getTagsColorKey(cat.name, group.name),
                            color: group.color || '',
                        })
                    })
                })
                this.$emit('refresh-group-tags', {colors})
            }).catch(() => {
                this.saving = false
                this.$toastr.error(this.getLang('failed'))
            })
        },
    },
}
</script>
