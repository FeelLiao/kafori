<template>
  <!-- 左侧导航菜单：固定定位 -->
  <nav class="aside fixed left-0 top-16 h-[calc(100vh-4rem)] w-60 bg-white dark:bg-gray-900 shadow-xl flex flex-col pt-10 z-20 border-r border-gray-200 dark:border-gray-800">
    <h2 class="text-lg font-bold text-center mb-10 text-green-700 dark:text-green-300 tracking-wider">
      {{$t('Transcripts_nav')}}
    </h2>
    <ul class="space-y-6 px-8">
      <li>
        <button
            class="w-full text-left font-medium py-2 px-3 rounded-lg transition-colors duration-200 hover:bg-green-100 dark:hover:bg-gray-800 focus:outline-none"
            :class="{ 'bg-green-100 dark:bg-gray-800': activeSection === 'experiment' }"
            @click="$emit('navigate', 'experiment')"
        >
          🧪 {{$t('Transcripts_experiment')}}
        </button>
      </li>
      <li>
        <button
            class="w-full text-left font-medium py-2 px-3 rounded-lg transition-colors duration-200 hover:bg-blue-100 dark:hover:bg-gray-800 focus:outline-none"
            :class="{ 'bg-blue-100 dark:bg-gray-800': activeSection === 'sample' }"
            @click="$emit('navigate', 'sample')"
        >
          🧬 {{$t('Transcripts_sample')}}
        </button>
      </li>
      <li>
        <button
            class="w-full text-left font-medium py-2 px-3 rounded-lg transition-colors duration-200 hover:bg-gray-100 dark:hover:bg-gray-800 focus:outline-none"
            :class="{ 'bg-gray-100 dark:bg-gray-800': activeSection === 'result' }"
            @click="$emit('navigate', 'result')"
        >
          📊 {{$t('Transcripts_result')}}
        </button>
      </li>
    </ul>
  </nav>
</template>

<script setup lang="ts">
defineProps<{
  activeSection: 'experiment' | 'sample' | 'result'
}>();
defineEmits<{
  (e: 'navigate', section: 'experiment' | 'sample' | 'result'): void
}>();
</script>

<style scoped>
.aside {
  box-shadow: 0 0 16px 0 rgba(60, 70, 100, 0.12);
}
</style>