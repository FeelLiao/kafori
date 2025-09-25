<!--<template>-->
<!--  &lt;!&ndash; 新增外层 wrapper &ndash;&gt;-->
<!--  <div class="header-wrapper bg-white border-b" :class="{ dark: isDark }">-->

<!--    <el-header class="top-nav">-->
<!--      &lt;!&ndash; 原有内容整体搬进来 ↓↓↓ &ndash;&gt;-->
<!--      &lt;!&ndash; 1️⃣ 顶部矩形 Logo 区 &ndash;&gt;-->
<!--      <div class="logo-bar">-->
<!--        <img src="@/assets/logo.svg" alt="Logo" class="logo-img" />-->
<!--        <span class="logo-text">Kafori</span>-->
<!--      </div>-->
<!--      &lt;!&ndash; 2️⃣ 原导航栏（完全不变） &ndash;&gt;-->

<!--      <div class="center-spacer" />-->
<!--      <el-menu-->
<!--          :default-active="activeIndex"-->
<!--          mode="horizontal"-->
<!--          :ellipsis="false"-->
<!--          class="nav-menu"-->
<!--          :background-color="isDark ? '#1f1f1f' : '#ffffff'"-->
<!--          :text-color="isDark ? '#e5e5e5' : '#303133'"-->
<!--          :active-text-color="isDark ? '#409eff' : '#409eff'"-->
<!--          @select="handleSelect"-->
<!--      >-->
<!--        <el-menu-item index="/"><el-icon><HomeFilled /></el-icon>Home</el-menu-item>-->
<!--        <el-menu-item index="/table"><el-icon><Reading /></el-icon>Transcripts</el-menu-item>-->
<!--        <el-menu-item index="/"><el-icon><Avatar /></el-icon>Pipeline</el-menu-item>-->
<!--        <el-menu-item index="/download"><el-icon><Headset /></el-icon>Download</el-menu-item>-->
<!--        <el-menu-item index="/"><el-icon><StarFilled /></el-icon>Tools</el-menu-item>-->
<!--        <el-menu-item index="/"><el-icon><UserFilled /></el-icon>Help</el-menu-item>-->
<!--        <el-menu-item index="/"><el-icon><UserFilled /></el-icon>Contact</el-menu-item>-->
<!--      </el-menu>-->
<!--      <div class="right-controls">-->
<!--        <el-button circle class="theme-btn" @click="toggleTheme">-->
<!--          <el-icon><Sunny v-if="isDark" /><Moon v-else /></el-icon>-->
<!--        </el-button>-->
<!--        <el-button circle class="hamburger" @click="drawer = true">-->
<!--          <el-icon><Menu /></el-icon>-->
<!--        </el-button>-->
<!--      </div>-->
<!--      <div class="ml-auto flex items-center gap-3"><Avatar_User /></div>-->
<!--    </el-header>-->

<!--  </div>-->
<!--</template>-->

<!--<script setup lang="ts">-->
<!--/* 原有逻辑 100% 不变 */-->
<!--import { ref, computed } from 'vue'-->
<!--import { useRouter, useRoute } from 'vue-router'-->
<!--import {-->
<!--  Menu, HomeFilled, Reading, Headset, Avatar, StarFilled, UserFilled, Sunny, Moon,-->
<!--} from '@element-plus/icons-vue'-->
<!--import Avatar_User from './components/avatar.vue'-->

<!--const router = useRouter()-->
<!--const route = useRoute()-->
<!--const drawer = ref(false)-->
<!--const activeIndex = computed(() => route.path)-->
<!--const isDark = ref(false)-->

<!--function toggleTheme() {-->
<!--  isDark.value = !isDark.value-->
<!--  document.documentElement.classList.toggle('dark', isDark.value)-->
<!--}-->
<!--function handleSelect(key: string) {-->
<!--  router.push(key)-->
<!--}-->
<!--</script>-->

<!--<style scoped>-->
<!--/* 顶层 wrapper 颜色跟随主题 */-->
<!--.header-wrapper {-->
<!--  background: var(&#45;&#45;nav-bg);-->
<!--  color: var(&#45;&#45;nav-text);-->
<!--  transition: background 0.3s, color 0.3s;-->

<!--  justify-content: center;-->
<!--}-->
<!--/* ===== 生物绿色主题变量 ===== */-->
<!--:root {-->
<!--  &#45;&#45;nav-bg: #ffffff;-->
<!--  &#45;&#45;nav-text: #2e7d32;        /* 森林绿 */-->
<!--  &#45;&#45;border-color: #a5d6a7;    /* 浅绿边框 */-->
<!--  &#45;&#45;accent: #4caf50;          /* 主绿高亮 */-->
<!--}-->
<!--html.dark {-->
<!--  &#45;&#45;nav-bg: #1b1b1b;-->
<!--  &#45;&#45;nav-text: #a5d6a7;        /* 暗色文字 */-->
<!--  &#45;&#45;border-color: #2e7d32;-->
<!--  &#45;&#45;accent: #66bb6a;          /* 暗色高亮 */-->
<!--}-->

<!--/* 顶部 Logo 区 */-->
<!--.logo-bar {-->
<!--  display: flex;-->
<!--  align-items: center;-->
<!--  justify-content: flex-start; /* 修改为靠左对齐 */-->
<!--  gap: 12px;-->
<!--  padding: 12px 16px;-->
<!--  height: 64px;-->
<!--  border-bottom: 1px solid var(&#45;&#45;border-color);-->
<!--  margin-left: -200px;  /* 设置左边距 */-->
<!--  //background-color: #f1f8e9;          /* 淡绿底 */-->
<!--}-->
<!--html.dark .logo-bar {-->
<!--  background-color: var(&#45;&#45;border-color);          /* 暗绿底 */-->
<!--}-->

<!--/* logo-bar 与 header 左对齐 */-->


<!--.logo-img {-->
<!--  height: 50px;-->
<!--  width: auto;-->
<!--}-->
<!--.logo-text {-->
<!--  font-size: 25px;-->
<!--  font-weight: 600;-->
<!--  color: var(&#45;&#45;nav-text);-->
<!--}-->

<!--/* 导航栏 */-->
<!--.top-nav {-->
<!--  display: flex;   /* 宽度靠内容撑开 */-->
<!--  align-items: center;-->
<!--  justify-content: space-between;-->
<!--  padding: 0 200px;-->
<!--  height: 60px;-->
<!--  background: var(&#45;&#45;nav-bg);-->
<!--  color: var(&#45;&#45;nav-text);-->
<!--  transition: background 0.3s, color 0.3s;-->
<!--}-->



<!--/* 菜单高亮改为绿色 */-->
<!--.nav-menu {-->
<!--  flex: 1;-->
<!--  display: flex;-->
<!--  justify-content: center;-->
<!--  border: none;-->
<!--  ellipsis:false;-->
<!--}-->


<!--/* 鼠标触发hover颜色渐变 */-->
<!--.nav-menu .el-menu-item:hover,-->
<!--.nav-menu .el-menu-item:hover .el-icon {-->
<!--  color: #46a24c !important;-->
<!--}-->

<!--/* 当前激活项始终保持绿色 */-->
<!--.nav-menu .el-menu-item.is-active,-->
<!--.nav-menu .el-menu-item.is-active .el-icon {-->
<!--  color: #46a24c !important;-->
<!--  border-bottom-color: #46a24c !important;-->
<!--}-->

<!--/* 让整栏更饱满 */-->
<!--.nav-menu .el-menu-item {-->
<!--  font-size: 18px;-->
<!--  font-weight: 600;-->
<!--  letter-spacing: 0.5px;-->
<!--}-->
<!--.right-controls .el-button .el-icon {-->
<!--  font-size: 20px;-->
<!--}-->

<!--/* 按钮颜色 */-->
<!--.theme-btn,-->
<!--.hamburger {-->
<!--  color: var(&#45;&#45;nav-text);-->
<!--  background: transparent;-->
<!--  border: 1px solid var(&#45;&#45;border-color);-->
<!--}-->
<!--.theme-btn:hover,-->
<!--.hamburger:hover {-->
<!--  background: var(&#45;&#45;accent);-->
<!--  color: #fff;-->
<!--}-->

<!--/* 响应式折叠 */-->
<!--@media (max-width: 1100px) {-->
<!--  .nav-menu { display: none; }-->
<!--}-->
<!--@media (min-width: 0px) {-->
<!--  .hamburger { display: none; }-->
<!--}-->



<!--</style>-->


<template>
  <nav class="bg-white dark:bg-black text-black dark:text-white shadow-lg">
    <div class="max-w-7xl mx-auto px-4">
      <div class="flex justify-between h-16">
        <!-- Logo区域 -->
        <div class="flex items-center">
          <!-- 生物图标 -->
          <div class="flex-shrink-0 flex items-center">
            <div class="w-8 h-8 bg-black dark:bg-white rounded-full flex items-center justify-center mr-2">
              <div class="w-4 h-4 border-2 border-white dark:border-black rounded-full"></div>
            </div>
            <span class="font-bold tracking-wider">BioDataHub</span>
          </div>

          <!-- 导航链接 -->
          <div class="hidden md:ml-6 md:flex md:space-x-8">
            <router-link to="/" class="inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium hover:text-black hover:border-gray-300 dark:hover:text-white dark:hover:border-gray-500" active-class="border-black">{{$t("nav_Home")}}</router-link>
            <router-link to="/Transcripts" class="inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium hover:text-black hover:border-gray-300 dark:hover:text-white dark:hover:border-gray-500" active-class="border-black">{{$t("nav_Transcripts")}}</router-link>
            <router-link to="/Pipelines" class="inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium hover:text-black hover:border-gray-300 dark:hover:text-white dark:hover:border-gray-500" active-class="border-black">{{$t("nav_Pipeline")}}</router-link>
            <router-link to="/Download" class="inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium hover:text-black hover:border-gray-300 dark:hover:text-white dark:hover:border-gray-500" active-class="border-black">{{$t("nav_Download")}}</router-link>
            <router-link to="/Tools" class="inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium hover:text-black hover:border-gray-300 dark:hover:text-white dark:hover:border-gray-500" active-class="border-black">{{$t("nav_Tools")}}</router-link>
            <router-link to="/Help" class="inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium hover:text-black hover:border-gray-300 dark:hover:text-white dark:hover:border-gray-500" active-class="border-black">{{$t("nav_Help")}}</router-link>
            <router-link to="/Contact" class="inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium hover:text-black hover:border-gray-300 dark:hover:text-white dark:hover:border-gray-500" active-class="border-black">{{$t("nav_Contact")}}</router-link>

          </div>
        </div>

        <!-- 右侧操作区 -->
        <div class="flex items-center">
          <!-- 主题切换按钮 -->
          <div class="mr-2">
            <button
                @click="toggleTheme"
                class="flex items-center justify-center w-9 h-9 rounded-full bg-gray-800 dark:bg-gray-200 text-white dark:text-black focus:outline-none transition duration-300"
                title="切换主题"
            >
              <svg v-if="isDarkMode" class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" />
              </svg>
              <svg v-else class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
              </svg>
            </button>
          </div>

          <!-- 用户头像 -->
          <div class="ml-2 flex items-center gap-3">
            <Avatar_User />
          </div>

          <!-- 语言切换 -->
          <div class="ml-2 relative">
            <el-select
                v-model="value"
                placeholder="English"
                class="w-full"
                :class="{
          'dark:bg-gray-800 dark:border-gray-700 dark:text-white': isDarkMode,
          'bg-white border-gray-300 text-gray-800': !isDarkMode,
        }"
                style="width: 100px"
                @change="setLang(value)"
            >
              <el-option
                  v-for="option in options"
                  :key="option.value"
                  :label="option.label"
                  :value="option.value"
              />
            </el-select>
          </div>
        </div>
      </div>
    </div>


  </nav>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
const router = useRouter();
import Avatar_User from './components/avatar.vue'
import Language_Switcher from '@/components/Common/LanguageSwitcher.vue'
import { useLangSwitcher } from '@/utils/index.ts';
const { setLang } = useLangSwitcher();


const handleSelect = (key: string) => {
  router.push(key);
}

const mobileMenuOpen = ref(false);
const isDarkMode = ref(false);

const toggleTheme = () => {
  if (isDarkMode.value) {
    disableDarkMode();
  } else {
    enableDarkMode();
  }
};

const enableDarkMode = () => {
  document.documentElement.classList.add('dark');
  isDarkMode.value = true;
  localStorage.setItem('theme', 'dark');
};

const disableDarkMode = () => {
  document.documentElement.classList.remove('dark');
  isDarkMode.value = false;
  localStorage.setItem('theme', 'light');
};

const value = ref('')
const options = [
  {
    value: 'zh',
    label: '中文',
  },
  {
    value: 'en',
    label: 'English',
  }
];

onMounted(() => {
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme === 'dark') {
    enableDarkMode();
  } else {
    disableDarkMode();
  }
});
</script>

<style scoped>
/* 亮色模式下的样式 */
.border-black {
  border-bottom: 2px solid black !important;
}

/* 暗色模式下的样式 */
html.dark .border-black {
  border-bottom: 2px solid white !important;
}
</style>