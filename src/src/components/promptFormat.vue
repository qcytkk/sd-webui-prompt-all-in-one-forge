<template>
    <div :class="['physton-prompt-format', {'embedded-host': embedded}]" v-if="isOpen" @click="close">
        <div class="format-main" @click.stop>
            <div class="format-close" v-if="!embedded" @click="close">
                <icon-svg name="close"/>
            </div>
            <div class="format-list" @click.stop>
                <!-- 行样式与【通用设置】一致：左=标题+详情，右=胶囊开关 -->
                <div class="settings-section" v-for="group in groups" :key="group.title">
                    <div class="settings-section-title" role="heading" aria-level="3">{{ getLang(group.title) }}</div>
                    <template v-for="item in group.items" :key="item.name">
                        <div class="setting-line"
                             v-if="!item.showWhen || this[item.showWhen]"
                             :class="{'paio-fmt-sub': item.sub}">
                            <div class="line-text">
                                <div class="line-title">{{ getLang(item.title) }}</div>
                                <div class="line-desc" v-html="getLang(item.desc)"></div>
                            </div>
                            <div class="line-content">
                                <div class="paio-pill" role="radiogroup" :aria-label="getLang(item.title)">
                                    <label class="paio-pill-btn">
                                        <input class="paio-pill-input" type="radio" :name="'paio-fmt-' + item.name"
                                               :checked="!this[item.name]"
                                               @change="setOpt(item.name, false)">
                                        <span>{{ getLang('toggle_off') }}</span>
                                    </label>
                                    <label class="paio-pill-btn">
                                        <input class="paio-pill-input" type="radio" :name="'paio-fmt-' + item.name"
                                               :checked="this[item.name]"
                                               @change="setOpt(item.name, true)">
                                        <span>{{ getLang('toggle_on') }}</span>
                                    </label>
                                </div>
                            </div>
                        </div>
                    </template>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
import LanguageMixin from "@/mixins/languageMixin";
import IconSvg from "@/components/iconSvg.vue";

export default {
    name: 'PromptFormat',
    components: {IconSvg},
    mixins: [LanguageMixin],
    props: {
        embedded: {type: Boolean, default: false},
        autoRemoveSpace: {
            type: Boolean,
            default: false,
        },
        autoRemoveLastComma: {
            type: Boolean,
            default: false,
        },
        autoKeepWeightZero: {
            type: Boolean,
            default: false,
        },
        autoKeepWeightOne: {
            type: Boolean,
            default: false,
        },
        autoBreakBeforeWrap: {
            type: Boolean,
            default: false,
        },
        autoBreakAfterWrap: {
            type: Boolean,
            default: false,
        },
        autoRemoveLoraBeforeComma: {
            type: Boolean,
            default: false,
        },
        autoRemoveLoraAfterComma: {
            type: Boolean,
            default: false,
        },
        useNovelAiWeightSymbol: {
            type: Boolean,
            default: false,
        },
        autoRemoveBeforeLineComma: {
            type: Boolean,
            default: false,
        },
        autoSplitByPeriod: {
            type: Boolean,
            default: false,
        },
        autoSplitByPeriodIncludeParen: {
            type: Boolean,
            default: false,
        },
    },
    data() {
        return {
            isOpen: false,
            // 行数据：name 与 props 名一一对应（用于 this[name] 取值与 update:<name> 事件）
            groups: [
                {
                    title: 'group_comma_space', items: [
                        {name: 'autoRemoveSpace', title: 'fmt_remove_space', desc: 'is_remove_space'},
                        {name: 'autoRemoveLastComma', title: 'fmt_remove_last_comma', desc: 'is_remove_last_comma'},
                        {name: 'autoRemoveBeforeLineComma', title: 'fmt_remove_before_line_comma', desc: 'is_remove_before_line_comma'},
                    ]
                },
                {
                    title: 'group_weight_symbol', items: [
                        {name: 'autoKeepWeightZero', title: 'fmt_keep_weight_zero', desc: 'is_keep_weight_zero'},
                        {name: 'useNovelAiWeightSymbol', title: 'fmt_novel_ai_symbol', desc: 'is_use_novel_ai_weight_symbol'},
                    ]
                },
                {
                    title: 'group_break_wrap', items: [
                        {name: 'autoBreakBeforeWrap', title: 'fmt_break_before_wrap', desc: 'is_break_before_wrap'},
                        {name: 'autoBreakAfterWrap', title: 'fmt_break_after_wrap', desc: 'is_break_after_wrap'},
                    ]
                },
                {
                    title: 'group_lora_period', items: [
                        {name: 'autoRemoveLoraBeforeComma', title: 'fmt_lora_before_comma', desc: 'is_remove_lora_before_comma'},
                        {name: 'autoRemoveLoraAfterComma', title: 'fmt_lora_after_comma', desc: 'is_remove_lora_after_comma'},
                        {name: 'autoSplitByPeriod', title: 'fmt_split_by_period', desc: 'is_split_by_period'},
                        {
                            name: 'autoSplitByPeriodIncludeParen', title: 'fmt_split_include_paren',
                            desc: 'is_split_by_period_include_paren', sub: true, showWhen: 'autoSplitByPeriod'
                        },
                    ]
                },
            ],
        }
    },
    emits: [
        'update:autoRemoveSpace',
        'update:autoRemoveLastComma',
        'update:autoKeepWeightZero',
        'update:autoKeepWeightOne',
        'update:autoBreakBeforeWrap',
        'update:autoBreakAfterWrap',
        'update:autoRemoveLoraBeforeComma',
        'update:autoRemoveLoraAfterComma',
        'update:useNovelAiWeightSymbol',
        'update:autoRemoveBeforeLineComma',
        'update:autoSplitByPeriod',
        'update:autoSplitByPeriodIncludeParen',
    ],
    computed: {},
    mounted() {
    },
    methods: {
        open() {
            this.isOpen = true
        },
        close() {
            this.isOpen = false
        },
        setOpt(name, value) {
            this.$emit('update:' + name, value)
        },
    },
}
</script>