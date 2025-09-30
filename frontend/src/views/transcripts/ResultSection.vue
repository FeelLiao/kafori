<template>
  <section class="mb-16">
    <div class="rounded-2xl shadow-xl bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 p-8 mb-8">
      <div class="flex items-center gap-4 mb-6">
        <span class="text-xl font-bold text-blue-700 dark:text-blue-300 tracking-wide">📊 {{$t('Transcripts_result')}}</span>
      </div>

      <div class="flex flex-wrap gap-8 justify-center items-center">
        <div
            v-for="plot in (res?.plots || [])"
            :key="plot.title"
            class="plot-block bg-gray-100 dark:bg-gray-800 rounded-xl shadow p-4 transition-all flex flex-col items-center"
            :style="{ marginBottom: '32px' }"
        >
          <div class="font-bold text-base mb-3 text-green-700 dark:text-green-300 flex items-center">
            <span class="mr-2">🧬</span>{{ plot.title }}
          </div>
          <el-image
              :src="`data:${plot.format},${plot.data}`"
              fit="contain"
              :style="{ width: width + 'px', height: height + 'px', borderRadius: '10px', border: '1px solid #eaeaea' }"
              class="transition-all duration-300 hover:shadow-xl"
          />
        </div>
      </div>

      <div v-for="(tableData, tableKey) in tables" :key="tableKey" class="mb-8">
        <div class="font-bold text-lg mb-2 text-gray-700 dark:text-gray-200">{{ tableKey }}</div>
        <re-pure-table
            :data="tableData"
            :columns="getColumns(tableData)"
            :full-width="true"
            auto-column-width
            expand-to-fit
            fit
            :expand-skip-types="true"
            :min-auto-col-width="50"
            :max-auto-col-width="1000"
            :char-pixel="12"
            single-line
            :show-pagination="false"
        />
        <el-button type="success" @click="exportCSV(tableKey)">导出 {{ tableKey }} CSV</el-button>
      </div>

    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import RePureTable from '@/components/re-pure-table.vue';

const props = defineProps<{
  res: any;
  width: number;
  height: number;
}>();

// 动态获取所有表
const tables = computed(() => props.res?.tables || {});

// 动态生成列
function getColumns(data: any[]) {
  if (!data || !data.length) return [];
  return Object.keys(data[0]).map(key => ({
    prop: key,
    label: key
  }));
}

// 导出指定表的 CSV
function exportCSV(tableKey: string) {
  const data = tables.value[tableKey] || [];
  if (!data.length) return;
  const columns = getColumns(data);
  const headers = columns.map(col => col.label);
  const keys = columns.map(col => col.prop);
  const rows = data.map(row => keys.map(k => row[k]));
  const csvContent = [headers, ...rows]
      .map(r => r.map(v => `"${String(v ?? '')}"`).join(','))
      .join('\r\n');
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${tableKey}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}
</script>
<style scoped>
.plot-block { min-width: 300px; max-width: 1050px; }
</style>