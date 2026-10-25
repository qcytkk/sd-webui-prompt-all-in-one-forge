import common from "@/utils/common"
import Papa from 'papaparse'
import globals from "../../globals";

// 标签词典 CSV 常见的首行表头（如「英文,中文」「name,zh_CN」），解析时跳过，避免被当成词条
const CSV_HEADERS = new Set([
    '英文|中文',
    'english|chinese',
    'english|zh',
    'english|zh_cn',
    'name|zh_cn',
    'tag|zh_cn',
    'name|translation',
    'tag|translation',
])

export default {
    props: {
        languageCode: {
            type: String,
            default: 'en_US'
        },
        languages: {
            type: Object,
            default: () => {
            },
        },
        translateApis: {
            type: Array,
            default: () => [],
        },
        translateApi: {
            type: String,
            default: '',
        },
        translateApiConfig: {
            type: Object
        },
        tagCompleteFile: {
            type: String,
            default: ''
        },
        onlyCsvOnAuto: {
            type: Boolean,
            default: false
        },
        groupTagsTranslate: {
            type: Boolean,
            default: true
        },
        // 翻译流程：五个翻译方案的可启用状态与先后顺序（数组顺序即尝试顺序）
        translateFlow: {
            type: Array,
            default: () => []
        },
        groupTagsTranslateCache: {
            type: Object,
            default: () => {
                return {
                    toEn: new Map(),
                    toLocal: new Map()
                }
            },
        },
    },
    data() {
        return {
            cancelMultiTranslate: false,
            globals: globals
        }
    },
    computed: {
        langName() {
            for (const key in this.languages) {
                const item = this.languages[key]
                if (item.code === this.languageCode) {
                    return item.name
                }
            }
            return item.name
        }
    },
    methods: {
        getLang(key) {
            return common.getLang(key, this.languageCode, this.languages)
        },
        replaceGlobals(text) {
            return common.replaceGlobals(text, this.languageCode)
        },
        getCSV(tagCompleteFile = null, reload = false) {
            window.tagCompleteFileCache = window.tagCompleteFileCache || {}
            window.tagCompleteFileLoading = window.tagCompleteFileLoading || {}
            return new Promise((resolve, reject) => {
                tagCompleteFile = tagCompleteFile || this.tagCompleteFile
                if (!reload && window.tagCompleteFileCache[tagCompleteFile]) {
                    // 缓存命中时先按文件 mtime+size 判断是否被外部增改，有变化才重读
                    this.ensureCSVFresh(tagCompleteFile).then(() => {
                        resolve(window.tagCompleteFileCache[tagCompleteFile])
                    })
                    return
                }

                // 判断是否获取csv中
                if (window.tagCompleteFileLoading[tagCompleteFile]) {
                    const timer = setInterval(() => {
                        if (!window.tagCompleteFileLoading[tagCompleteFile]) {
                            clearInterval(timer)
                            resolve(window.tagCompleteFileCache[tagCompleteFile])
                        }
                    }, 100)
                    return
                }
                window.tagCompleteFileLoading[tagCompleteFile] = true

                let data = {toEn: new Map(), toLocal: new Map()}
                let setData = (en, local) => {
                    const texts = [
                        en,
                        en.replace(/\_/g, ' '),
                        en.replace(/\-/g, ' '),
                    ]
                    texts.forEach(t => data.toLocal.set(t, local))
                    data.toEn.set(local, en)
                    // console.log('setData:csv', local, key, en)
                }

                if (!tagCompleteFile) {
                    if (typeof translations === 'object' && translations instanceof Map) {
                        translations.forEach((local, en) => {
                            setData(en, local)
                        })
                        window.tagCompleteFileLoading[tagCompleteFile] = false
                        window.tagCompleteFileCache[tagCompleteFile] = data
                        resolve(data)
                        return
                    }
                }

                if (!tagCompleteFile) {
                    window.tagCompleteFileLoading[tagCompleteFile] = false
                    window.tagCompleteFileCache[tagCompleteFile] = data
                    reject(this.getLang('not_found_csv_file'))
                    return
                }

                this.gradioAPI.getCSV(tagCompleteFile).then(res => {
                    res = Papa.parse(res, {
                        header: false,
                        skipEmptyLines: true,
                    })
                    res.data.forEach((line, index) => {
                        if (line.length < 2) return
                        let en = line[0].trim()
                        let local = line[1].trim()
                        if (en === '' || local === '') return
                        // 首行是表头时跳过（有的词典 CSV 带表头，有的不带，两种都兼容）
                        if (index === 0) {
                            const head = en.toLowerCase().replace(/^\uFEFF/, '')
                            if (CSV_HEADERS.has(`${head}|${local.toLowerCase()}`)) return
                        }
                        setData(en, local)
                    })

                    /*res = res.replace(/\r/g, '\n')
                    let lines = res.split('\n')
                    lines.forEach(line => {
                        if (line === '') return
                        if (line.trim() === '') return
                        let items = line.split(',')
                        if (items.length < 2) return
                        let en = items[0].trim()
                        let local = items[1].trim()
                        if (en === '' || local === '') return
                        setData(en, local)
                    })*/
                    window.tagCompleteFileLoading[tagCompleteFile] = false
                    window.tagCompleteFileCache[tagCompleteFile] = data
                    window.tagCompleteFileCacheAt = window.tagCompleteFileCacheAt || {}
                    window.tagCompleteFileCacheAt[tagCompleteFile] = Date.now()
                    resolve(data)
                }).catch(error => {
                    window.tagCompleteFileLoading[tagCompleteFile] = false
                    window.tagCompleteFileCache[tagCompleteFile] = data
                    if (error.response && error.response.status === 404) {
                        reject(this.getLang('not_found_csv_file'))
                    } else {
                        reject(error.message)
                    }
                })
            })
        },
        // 标签词典文件也可能被其它插件/手工增改：翻译前按 mtime+size 判断缓存是否过期，
        // 只有真的变了才重新下载解析，避免每次翻译都白解析整份大 CSV
        ensureCSVFresh(key) {
            if (!key) return Promise.resolve()
            window.tagCompleteFileMeta = window.tagCompleteFileMeta || {}
            window.tagCompleteFileChecking = window.tagCompleteFileChecking || {}
            window.tagCompleteFileCacheAt = window.tagCompleteFileCacheAt || {}
            const meta = window.tagCompleteFileMeta[key] || {}
            // 2 秒内已检查过：同一批翻译里的多个标签共用一次结果
            if (meta.checkedAt && Date.now() - meta.checkedAt < 2000) return Promise.resolve()
            if (window.tagCompleteFileChecking[key]) return window.tagCompleteFileChecking[key]
            const task = this.gradioAPI.getCSVs().then(csvs => {
                meta.checkedAt = Date.now()
                window.tagCompleteFileMeta[key] = meta
                const file = (csvs || []).find(item => item.key === key)
                if (!file) {
                    // 文件被删除或改名：清掉缓存，后续按原逻辑处理
                    delete window.tagCompleteFileCache[key]
                    delete window.tagCompleteFileCacheAt[key]
                    return
                }
                const sig = `${file.mtime}|${file.size}`
                if (meta.sig === sig) return
                // 首次检查：若缓存是在文件最后修改之后加载的，说明缓存就是最新内容
                const cacheAt = window.tagCompleteFileCacheAt[key] || 0
                meta.sig = sig
                if (!cacheAt || cacheAt < file.mtime) {
                    const oldCache = window.tagCompleteFileCache[key]
                    return this.getCSV(key, true).catch(() => {
                        // 重读失败时保留旧缓存，避免整批翻译静默失配
                        if (oldCache) window.tagCompleteFileCache[key] = oldCache
                    })
                }
            }).catch(() => {
                // 接口不可用时不阻塞翻译，继续使用已有缓存
            }).then(() => {
                delete window.tagCompleteFileChecking[key]
            })
            window.tagCompleteFileChecking[key] = task
            return task
        },
        _translateToLocalBy(text, toLocal, useNetwork = false) {
            text = text.trim().toLowerCase()
            let _localToString = value => (value.join?.(' / ') ?? value)
            if (toLocal.has(text)) {
                return _localToString(toLocal.get(text))
            } else {
                // 使用 , 分隔
                const texts = text.split(',').map(t => t.trim())
                let result = []
                let needs = []
                texts.forEach(t => {
                    if (toLocal.has(t)) {
                        result.push(_localToString(toLocal.get(t)))
                    } else if (useNetwork && t.length) {
                        needs.push(t)
                    }
                })
                if (result.length > 0 && !needs.length) return result.join(', ')
            }
            return ''
        },
        async translateToLocalByCSV(text, tagCompleteFile = null, reload = false, useNetwork = false) {
            let res = await this.getCSV(tagCompleteFile, reload)
            return this._translateToLocalBy(text, res.toLocal, useNetwork)
        },
        async translateToEnByCSV(text, tagCompleteFile = null, reload = false) {
            let res = await this.getCSV(tagCompleteFile, reload)
            return this._toEn(text, res.toEn)
        },
        async translateToLocalByGroupTags(text, useNetwork = false) {
            console.log('translateToLocalByGroupTags', text)
            return this._translateToLocalBy(text, this.groupTagsTranslateCache.toLocal, useNetwork)
        },
        async translateToEnByGroupTags(text) {
            return this._toEn(text, this.groupTagsTranslateCache.toEn)
        },
        _toEn(text, toEn) {
            text = text.trim().toLowerCase()
            if (toEn.has(text)) {
                return toEn.get(text)
            }
            return ''
        },
    }
}
