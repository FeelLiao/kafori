<script setup lang="ts">
import { ref, watch } from 'vue'
import MarkdownIt from 'markdown-it'
import 'github-markdown-css/github-markdown.css'
import i18n from '@/i18n'

const md = new MarkdownIt()
const renderedHtml = ref('')
const isCentered = ref(false)

async function loadMarkdown(lang: string) {
  const file = lang === 'zh' ? '/src/assets/md/help_zh.md' : '/src/assets/md/help_en.md'
  const res = await fetch(file)
  const text = await res.text()
  renderedHtml.value = md.render(text)
}

// 初始化和监听语言切换
watch(i18n.global.locale, (lang) => {
  loadMarkdown(lang)
}, { immediate: true })

</script>

<template>
  <div>
    <div
        class="markdown-body"
        :class="{ centered: isCentered }"
        v-html="renderedHtml"
    ></div>
  </div>
</template>

<style scoped>
.markdown-body {
  background: var(--el-bg-color, #fff);
  color: var(--el-text-color-primary, #222);
  padding: 32px;
  border-radius: 12px;
  box-shadow: 0 2px 16px rgba(0,0,0,0.08);
  font-size: 16px;
  line-height: 1.8;
  transition: all 0.2s;
}
.markdown-body img {
  max-width: 100%;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  display: block;
  margin: 24px auto;
}
.markdown-body.centered {
  text-align: center;
}
</style>
