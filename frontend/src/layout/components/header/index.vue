<template>
  <!-- 新增外层 wrapper -->
  <div class="header-wrapper" :class="{ dark: isDark }">
    <!-- 1️⃣ 顶部矩形 Logo 区 -->
    <div class="logo-bar">
      <img src="@/assets/logo.svg" alt="Logo" class="logo-img" />
      <span class="logo-text">Larix kaempferi Transcriptome DataBase</span>
    </div>
    <!-- 2️⃣ 原导航栏（完全不变） -->
    <el-header class="top-nav">
      <!-- 原有内容整体搬进来 ↓↓↓ -->
      <div class="center-spacer" />
      <el-menu
          :default-active="activeIndex"
          mode="horizontal"
          :ellipsis="false"
          class="nav-menu"
          :background-color="isDark ? '#1f1f1f' : '#ffffff'"
          :text-color="isDark ? '#e5e5e5' : '#303133'"
          :active-text-color="isDark ? '#409eff' : '#409eff'"
          @select="handleSelect"
      >
        <el-menu-item index="/"><el-icon><HomeFilled /></el-icon>Home</el-menu-item>
        <el-menu-item index="/table"><el-icon><Reading /></el-icon>Transcripts</el-menu-item>
        <el-menu-item index="/"><el-icon><Avatar /></el-icon>Pipeline</el-menu-item>
        <el-menu-item index="/download"><el-icon><Headset /></el-icon>Download</el-menu-item>
        <el-menu-item index="/"><el-icon><StarFilled /></el-icon>Tools</el-menu-item>
        <el-menu-item index="/"><el-icon><UserFilled /></el-icon>Help</el-menu-item>
        <el-menu-item index="/"><el-icon><UserFilled /></el-icon>Contact</el-menu-item>
      </el-menu>
      <div class="right-controls">
        <el-button circle class="theme-btn" @click="toggleTheme">
          <el-icon><Sunny v-if="isDark" /><Moon v-else /></el-icon>
        </el-button>
        <el-button circle class="hamburger" @click="drawer = true">
          <el-icon><Menu /></el-icon>
        </el-button>
      </div>
    </el-header>

  </div>
</template>

<script setup lang="ts">
/* 原有逻辑 100% 不变 */
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  Menu, HomeFilled, Reading, Avatar, Headset, StarFilled, UserFilled, Sunny, Moon,
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const drawer = ref(false)
const activeIndex = computed(() => route.path)
const isDark = ref(false)

function toggleTheme() {
  isDark.value = !isDark.value
  document.documentElement.classList.toggle('dark', isDark.value)
}
function handleSelect(key: string) {
  router.push(key)
}
</script>

<style scoped>
/* 顶层 wrapper 颜色跟随主题 */
.header-wrapper {
  background: var(--nav-bg);
  color: var(--nav-text);
  transition: background 0.3s, color 0.3s;

  justify-content: center;
}
/* ===== 生物绿色主题变量 ===== */
:root {
  --nav-bg: #ffffff;
  --nav-text: #2e7d32;        /* 森林绿 */
  --border-color: #a5d6a7;    /* 浅绿边框 */
  --accent: #4caf50;          /* 主绿高亮 */
}
html.dark {
  --nav-bg: #1b1b1b;
  --nav-text: #a5d6a7;        /* 暗色文字 */
  --border-color: #2e7d32;
  --accent: #66bb6a;          /* 暗色高亮 */
}

/* 顶部 Logo 区 */
.logo-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 12px 16px;
  height: 64px;
  border-bottom: 1px solid var(--border-color);
  background-color: #f1f8e9;          /* 淡绿底 */
}
html.dark .logo-bar {
  background-color: var(--border-color);          /* 暗绿底 */
}

/* logo-bar 与 header 左对齐 */


.logo-img {
  height: 50px;
  width: auto;
}
.logo-text {
  font-size: 25px;
  font-weight: 600;
  color: var(--nav-text);
}

/* 导航栏 */
.top-nav {
  display: flex;   /* 宽度靠内容撑开 */
  align-items: center;
  justify-content: space-between;
  padding: 0 200px;
  height: 60px;
  background: var(--nav-bg);
  color: var(--nav-text);
  transition: background 0.3s, color 0.3s;
}



/* 菜单高亮改为绿色 */
.nav-menu {
  flex: 1;
  display: flex;
  justify-content: center;
  border: none;
  ellipsis:false;
}


/* 鼠标触发hover颜色渐变 */
.nav-menu .el-menu-item:hover,
.nav-menu .el-menu-item:hover .el-icon {
  color: #46a24c !important;
}

/* 当前激活项始终保持绿色 */
.nav-menu .el-menu-item.is-active,
.nav-menu .el-menu-item.is-active .el-icon {
  color: #46a24c !important;
  border-bottom-color: #46a24c !important;
}

/* 让整栏更饱满 */
.nav-menu .el-menu-item {
  font-size: 18px;
  font-weight: 600;
  letter-spacing: 0.5px;
}
.right-controls .el-button .el-icon {
  font-size: 20px;
}

/* 按钮颜色 */
.theme-btn,
.hamburger {
  color: var(--nav-text);
  background: transparent;
  border: 1px solid var(--border-color);
}
.theme-btn:hover,
.hamburger:hover {
  background: var(--accent);
  color: #fff;
}

/* 响应式折叠 */
@media (max-width: 1100px) {
  .nav-menu { display: none; }
}
@media (min-width: 0px) {
  .hamburger { display: none; }
}



</style>