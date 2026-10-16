<template>
    <Transition name="fade">
        <!-- 改为「插件设置」同款模态：固定遮罩 + 居中弹窗；只能点关闭按钮或遮罩关闭，
             不再鼠标移出/超时自动关闭（2026-10-17 @TraeCode） -->
        <div class="physton-prompt-favorite" v-show="isShow" @click="onMaskClick">
            <div class="paio-modal-main" @click.stop>
                <div class="paio-modal-header">
                    <div class="paio-modal-title">{{ getLang('favorite') }}</div>
                    <div class="paio-modal-close" role="button" tabindex="0"
                         :aria-label="getLang('close')" :title="getLang('close')"
                         @click="hide" @keydown.enter="hide" @keydown.space.prevent="hide">
                        <icon-svg name="close"/>
                    </div>
                </div>
                <div class="paio-modal-body">
                    <div class="popup-tabs">
                        <div v-for="(group) in favorites" :key="group.key"
                             :class="['popup-tab', group.key === favoriteKey ? 'active': '']" @click="onTabClick(group.key)">
                            <div class="tab-name">{{ getLang(group.name) }}</div>
                            <div class="tab-type">{{ getLang(group.type) }}</div>
                            <div class="tab-count">{{ group.list.length }}</div>
                        </div>
                    </div>
                    <div v-for="(group) in favorites" :key="group.key" :class="['popup-tab-content', group.key === favoriteKey ? 'active': '']">
                        <div class="content-list" v-show="group.list.length > 0">
                            <div class="content-item" v-for="(item, index) in group.list" :key="item.id"
                                 @mouseenter="onItemMouseEnter(index, $event)" @mouseleave="onItemMouseLeave(index)">
                                <div class="item-header">
                                    <div class="item-header-left">
                                        <div class="item-header-index">{{ group.list.length - index }}</div>
                                        <div class="item-header-time">{{ formatTime(item.time) }}</div>
                                        <div class="item-header-name">
                                            <input class="header-name-input" :value="item.name"
                                                   @keydown="onNameKeyDown(index, $event)"
                                                   @change="onNameChange(index, $event)" :placeholder="getLang('unset_name')">
                                        </div>
                                    </div>
                                    <div class="item-header-right">
                                        <div class="header-btn-favorite hover-scale-140" @click="onFavoriteClick(index)"
                                             v-show="item.is_favorite" v-tooltip="getLang('remove_from_favorite')">
                                            <icon-svg name="favorite-yes"/>
                                        </div>
                                        <div class="header-btn-favorite hover-scale-140" @click="onFavoriteClick(index)"
                                             v-show="!item.is_favorite" v-tooltip="getLang('add_to_favorite')">
                                            <icon-svg name="favorite-no"/>
                                        </div>
                                        <div class="header-btn-copy hover-scale-140" @click="onCopyClick(index)"
                                             v-tooltip="getLang('copy_to_clipboard')">
                                            <icon-svg name="copy"/>
                                        </div>
                                        <div class="header-btn-use hover-scale-140" @click="onUseClick(index)"
                                             v-tooltip="getLang('use')">
                                            <icon-svg name="use"/>
                                        </div>
                                        <div class="header-btn-move-up hover-scale-140" @click="onMoveUpClick(index)"
                                             v-tooltip="getLang('move_up')">
                                            <icon-svg name="move-up"/>
                                        </div>
                                        <div class="header-btn-move-down hover-scale-140" @click="onMoveDownClick(index)"
                                             v-tooltip="getLang('move_down')">
                                            <icon-svg name="move-down"/>
                                        </div>
                                    </div>
                                </div>
                                <div class="item-prompt">{{ item.prompt }}</div>
                            </div>
                        </div>
                        <div class="content-empty" v-show="group.list.length === 0">
                            <icon-svg name="loading" v-if="loading"/>
                            <span v-else>{{ emptyMsg }}</span>
                        </div>
                    </div>
                </div>
            </div>
            <!-- 条目悬停时的「标签预览」浮层：改为相对视口定位（JS 按悬停条目的位置算） -->
            <div class="popup-detail" ref="favoriteDetail" v-show="currentItem && currentItem.tags" @click.stop>
                <div class="popup-item-tags">
                    <template v-for="(tag, index) in currentItem.tags" :key="index">
                        <div v-if="tag.type && tag.type === 'wrap'" class="item-wrap"></div>
                        <div v-else class="item-tag">
                            <div class="item-tag-value">{{ tag.value }}</div>
                            <div class="item-tag-local-value">{{ tag.localValue }}</div>
                        </div>
                    </template>
                </div>
            </div>
        </div>
    </Transition>
</template>
<script>
import common from "@/utils/common";

import LanguageMixin from "@/mixins/languageMixin";
import IconSvg from "@/components/iconSvg.vue";
import waitTick from '@/utils/waitTick';

export default {
    components: {IconSvg},
    props: {},
    mixins: [LanguageMixin],
    data() {
        return {
            favoriteKey: '',
            favorites: [
                {
                    'name': 'txt2img',
                    'type': 'prompt',
                    'key': 'txt2img',
                    'list': [],
                },
                {
                    'name': 'txt2img',
                    'type': 'negative_prompt',
                    'key': 'txt2img_neg',
                    'list': [],
                },
                {
                    'name': 'img2img',
                    'type': 'prompt',
                    'key': 'img2img',
                    'list': [],
                },
                {
                    'name': 'img2img',
                    'type': 'negative_prompt',
                    'key': 'img2img_neg',
                    'list': [],
                },
            ],
            isShow: false,
            loading: false,
            emptyMsg: '',
            currentItem: {}
        }
    },
    emits: ['use'],
    mounted() {
        this.favorites.forEach(item => {
            waitTick.addWaitTick(() => this.getFavorites(item.key))
        })
    },
    beforeUnmount() {
        this.setScrollLock(false)
    },
    methods: {
        formatTime(time) {
            return common.formatTime(time * 1000, false)
        },
        getFavorites(favoriteKey) {
            if (!favoriteKey) return
            let favoriteItem = this.favorites.find(item => item.key === favoriteKey)
            if (!favoriteItem) return
            this.loading = true
            return this.gradioAPI.getFavorites(favoriteKey).then(res => {
                if(res && res.length > 0){
                    // 倒序
                    res.reverse()
                    res.forEach(item => {
                        item.is_favorite = true
                    })
                    favoriteItem.list = res
                }
                window.phystonPromptfavorites = this.favorites
                this.emptyMsg = this.getLang('no_favorite')
                this.loading = false
            }).catch(err => {
                this.emptyMsg = this.getLang('get_favorite_error')
                this.loading = false
            })
        },
        show(favoriteKey) {
            if (!favoriteKey) return
            this.favoriteKey = favoriteKey
            if (this.isShow) {
                this.hide()
                return
            }
            this.loading = true
            this.isShow = true
            this.setScrollLock(true)
            this.getFavorites(this.favoriteKey)
        },
        hide() {
            if (!this.isShow) return
            this.isShow = false
            this.currentItem = {}
            this.setScrollLock(false)
        },
        onMaskClick() {
            this.hide()
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
        onTabClick(key) {
            this.favoriteKey = key
            this.getFavorites(this.favoriteKey)
        },
        onFavoriteClick(index) {
            let group = this.favorites.find(item => item.key === this.favoriteKey)
            if (!group) return
            let favorite = group.list[index]
            if (!favorite.is_favorite) {
                this.gradioAPI.doFavorite(this.favoriteKey, favorite.id).then(res => {
                    if (res) {
                        favorite.is_favorite = true
                        window.phystonPromptfavorites = this.favorites
                    }
                })
            } else {
                this.gradioAPI.unFavorite(this.favoriteKey, favorite.id).then(res => {
                    if (res) {
                        favorite.is_favorite = false
                        window.phystonPromptfavorites = this.favorites
                    }
                })
            }
        },
        onCopyClick(index) {
            let group = this.favorites.find(item => item.key === this.favoriteKey)
            if (!group) return
            let favorite = group.list[index]
            this.$copyText(favorite.prompt).then(() => {
                this.$toastr.success("success!")
            }).catch(() => {
                this.$toastr.error("error!")
            })
        },
        onNameKeyDown(index, e) {
            if (e.keyCode === 13) {
                // 离开焦点
                e.target.blur()
            }
        },
        onNameChange(index, e) {
            let group = this.favorites.find(item => item.key === this.favoriteKey)
            if (!group) return
            let favorite = group.list[index]
            const value = e.target.value
            this.gradioAPI.setFavoriteName(this.favoriteKey, favorite.id, value).then(res => {
                if (res) {
                    favorite.name = value
                    window.phystonPromptfavorites = this.favorites
                } else {
                    e.target.value = favorite.name
                }
            }).catch(err => {
                e.target.value = favorite.name
            })
        },
        onItemMouseEnter(index, e) {
            let group = this.favorites.find(item => item.key === this.favoriteKey)
            if (!group) return
            this.currentItem = group.list[index]
            if (!this.currentItem || !this.currentItem.tags) return

            const itemEl = e && e.currentTarget ? e.currentTarget : null
            this.$nextTick(() => {
                const detail = this.$refs.favoriteDetail
                if (!detail || !itemEl) return
                // 弹窗已居中，浮层改为相对视口定位：贴在悬停条目右侧，放不下就翻到左侧
                const rect = itemEl.getBoundingClientRect()
                const dw = detail.offsetWidth || 400
                const dh = detail.offsetHeight || 0
                let left = rect.right + 8
                if (left + dw > window.innerWidth - 8) left = rect.left - dw - 8
                if (left < 8) left = 8
                let top = rect.top
                if (top + dh > window.innerHeight - 8) top = Math.max(8, window.innerHeight - dh - 8)
                detail.style.left = left + 'px'
                detail.style.top = top + 'px'
            })
        },
        onItemMouseLeave(index) {
            this.currentItem = {}
        },
        onUseClick(index) {
            let group = this.favorites.find(item => item.key === this.favoriteKey)
            if (!group) return
            this.hide()
            this.$emit('use', group.list[index])
        },
        onMoveUpClick(index) {
            let group = this.favorites.find(item => item.key === this.favoriteKey)
            if (!group) return
            let favorite = group.list[index]
            if (index === 0) return
            this.gradioAPI.moveDownFavorite(this.favoriteKey, favorite.id).then(res => {
            // this.gradioAPI.moveUpFavorite(this.favoriteKey, favorite.id).then(res => {
                if (res) {
                    group.list.splice(index, 1)
                    group.list.splice(index - 1, 0, favorite)
                    window.phystonPromptfavorites = this.favorites
                }
            })
        },
        onMoveDownClick(index) {
            let group = this.favorites.find(item => item.key === this.favoriteKey)
            if (!group) return
            let favorite = group.list[index]
            if (index === group.list.length - 1) return
            this.gradioAPI.moveUpFavorite(this.favoriteKey, favorite.id).then(res => {
            // this.gradioAPI.moveDownFavorite(this.favoriteKey, favorite.id).then(res => {
                if (res) {
                    group.list.splice(index, 1)
                    group.list.splice(index + 1, 0, favorite)
                    window.phystonPromptfavorites = this.favorites
                }
            })
        },
    }
}
</script>
