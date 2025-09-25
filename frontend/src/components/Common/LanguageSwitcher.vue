<template>
  <div class="relative">
    <el-select
        v-model="value"
        placeholder="英文"
        class="w-full"
        :class="{
        'dark:bg-gray-800 dark:border-gray-700 dark:text-white': isDarkMode,
        'bg-white border-gray-300 text-gray-800': !isDarkMode,
      }"
        style="width: 100px"
    >
      <el-option
          v-for="option in options"
          :key="option.value"
          :label="option.label"
          :value="option.value"
      />
    </el-select>
  </div>
</template>

<script setup lang="ts">


const options = [
  {
    value: 'Option1',
    label: '中文',
  },
  {
    value: 'Option2',
    label: '英文',
  },
];
</script>