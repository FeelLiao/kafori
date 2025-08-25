<template>
  <el-header class="top-nav" :class="{ dark: isDark }">

    <div class="logo">MyApp</div>
    <!-- 居中 Logo -->
    <!-- 1. Logo 固定在左 -->
    <router-link to="/" class="logo">

    </router-link>

    <!-- 2. 横向菜单：真正居中 -->
    <el-menu
        :default-active="activeIndex"
        mode="horizontal"
        class="nav-menu"
        :background-color="isDark ? '#1f1f1f' : '#ffffff'"
        :text-color="isDark ? '#e5e5e5' : '#303133'"
        :active-text-color="isDark ? '#409eff' : '#409eff'"
        @select="handleSelect"
    >
      <el-menu-item index="/"><el-icon><HomeFilled /></el-icon>首页</el-menu-item>
      <el-menu-item index="/library"><el-icon><Reading /></el-icon>文库</el-menu-item>
      <el-menu-item index="/artist"><el-icon><Avatar /></el-icon>艺人</el-menu-item>
      <el-menu-item index="/playlist"><el-icon><Headset /></el-icon>歌单</el-menu-item>
      <el-menu-item index="/like"><el-icon><StarFilled /></el-icon>收藏</el-menu-item>
      <el-menu-item index="/user"><el-icon><UserFilled /></el-icon>我的</el-menu-item>
    </el-menu>

    <!-- 3. 右侧按钮组固定不动 -->
    <div class="left-controls">
      <el-button circle class="theme-btn" @click="toggleTheme">
        <el-icon><Sunny v-if="isDark"/><Moon v-else/></el-icon>
      </el-button>
      <el-button circle class="hamburger" @click="drawer = true">
        <el-icon><Menu /></el-icon>
      </el-button>
    </div>

    <!-- 抽屉菜单（小屏）保持不变 -->
    <el-drawer v-model="drawer" direction="ltr" size="60%" :with-header="false">
      <el-menu
          :default-active="activeIndex"
          :background-color="isDark ? '#1f1f1f' : '#ffffff'"
          :text-color="isDark ? '#e5e5e5' : '#303133'"
          :active-text-color="isDark ? '#409eff' : '#409eff'"
          @select="(key)=>{handleSelect(key);drawer=false;}"
      >
        <el-menu-item index="/"><el-icon><HomeFilled /></el-icon>首页</el-menu-item>
        <el-menu-item index="/library"><el-icon><Reading /></el-icon>文库</el-menu-item>
        <el-menu-item index="/artist"><el-icon><Avatar /></el-icon>艺人</el-menu-item>
        <el-menu-item index="/playlist"><el-icon><Headset /></el-icon>歌单</el-menu-item>
        <el-menu-item index="/like"><el-icon><StarFilled /></el-icon>收藏</el-menu-item>
        <el-menu-item index="/user"><el-icon><UserFilled /></el-icon>我的</el-menu-item>
      </el-menu>
    </el-drawer>
  </el-header>
</template>

<script setup lang="ts">
import { ref, computed, watchEffect } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  Menu,
  HomeFilled,
  Reading,
  Avatar,
  Headset,
  StarFilled,
  UserFilled,
  Sunny,
  Moon,
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

const drawer = ref(false)
const activeIndex = computed(() => route.path)

// 主题状态
const isDark = ref(false)

// 切换主题
function toggleTheme() {
  isDark.value = !isDark.value
  document.documentElement.classList.toggle('dark', isDark.value)
}

// 响应式：窗口宽度变化自动关闭抽屉
const screenWidth = ref(window.innerWidth)
window.addEventListener('resize', () => {
  screenWidth.value = window.innerWidth
  if (screenWidth.value > 768) drawer.value = false
})

// 路由跳转
function handleSelect(key: string) {
  router.push(key)
}
</script>

<style scoped>
/* 变量：亮色/暗色 */
:root {
  --nav-bg: #ffffff;
  --nav-text: #303133;
}
html.dark {
  --nav-bg: #56b049;
  --nav-text: #e5e5e5;
}

.top-nav {
  display: flex;
  align-items: center;
  justify-content: space-between; /* 左右两栏固定，中间自动撑开 */
  padding: 0 16px;
}

.logo {
  flex-shrink: 0;          /* Logo 不压缩 */
}

.nav-menu {
  flex: 1 1 auto;
  display: flex;
  justify-content: center; /* 关键：菜单真正居中 */
  border: none;
}

.right-controls {
  flex-shrink: 0;          /* 按钮组不压缩 */
  display: flex;
  gap: 8px;
}

@media (max-width: 768px) {
  .nav-menu {
    display: none;
  }
}
@media (min-width: 769px) {
  .hamburger {
    display: none;
  }
}
</style>