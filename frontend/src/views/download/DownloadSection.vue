<script setup lang="ts">
import { ref, watch, computed, nextTick } from 'vue';
import type { UploadInstance, UploadProps } from 'element-plus';
import i18n from '@/i18n/index.ts'
import RePureTable from '@/components/re-pure-table.vue';
import { downloadFile } from '@/api/system.ts';
import type { Sample } from '@/api/interface.ts';

const props = defineProps<{
  samples: any[]
}>();
const emits = defineEmits<{
  (e: 'analyzed', payload: { res: any; width: number; height: number }): void
}>();

// 分页
const sample_pagination = ref({
  pageSize: 10,
  currentPage: 1,
  total: props.samples.length,
});
const pagedSamples = computed(() => {
  const start = (sample_pagination.value.currentPage - 1) * sample_pagination.value.pageSize;
  const end = start + sample_pagination.value.pageSize;
  return props.samples.slice(start, end);
});
const handleSamplePageChange = (page) => {
  sample_pagination.value.currentPage = page;
};
const handleSampleSizeChange = (size) => {
  sample_pagination.value.pageSize = size;
  sample_pagination.value.currentPage = 1;
};

// 受控多选（全局）
const selectedSampleIds = ref<string[]>([]);
const reTableRef = ref<any>();
const syncingSelection = ref(false);

// 单行选择/取消（增量维护全局）
function onSelectRow(selection: Sample[], row: Sample) {
  if (syncingSelection.value) return;
  const id = String(row.UniqueID);
  const checked = selection.some(r => String(r.UniqueID) === id);
  if (checked) {
    if (!selectedSampleIds.value.includes(id)) {
      selectedSampleIds.value = [...selectedSampleIds.value, id];
    }
  } else {
    selectedSampleIds.value = selectedSampleIds.value.filter(x => x !== id);
  }
}

// 全选/全不选（仅本页）
function onSelectAll(selection: Sample[]) {
  if (syncingSelection.value) return;
  const pageIds = pagedSamples.value.map(r => String(r.UniqueID));
  if (selection.length) {
    const set = new Set([...selectedSampleIds.value, ...pageIds]);
    selectedSampleIds.value = Array.from(set);
  } else {
    selectedSampleIds.value = selectedSampleIds.value.filter(id => !pageIds.includes(id));
  }
}

// 数据或分页变化时，对当前页按全局 keys 回显
watch(
    () => [pagedSamples.value, selectedSampleIds.value] as const,
    async () => {
      await nextTick();
      const table = reTableRef.value;
      if (!table?.syncSelectionByKeys) return;
      syncingSelection.value = true;
      try {
        await table.syncSelectionByKeys(selectedSampleIds.value);
      } finally {
        await nextTick();
        syncingSelection.value = false;
      }
    },
    { deep: true }
);

// 表格列
const sample_columns = computed(() =>[
  { prop: 'classes', label: i18n.global.t('Download_file_category') },
  { prop: 'item_type', label: i18n.global.t('Download_file') },
  { prop: 'filename', label: i18n.global.t('Download_file_name') },
  { prop: 'action', label: i18n.global.t('Download_file_action'), slot: 'action' }
]);

async function editRow(row: any) {
  let fileData = await downloadFile(row.classes, row.filename);
  // 如果不是 Blob，假设是 ArrayBuffer，转成 Blob
  if (!(fileData instanceof Blob)) {
    fileData = new Blob([fileData]);
  }
  const url = URL.createObjectURL(fileData);
  const a = document.createElement('a');
  a.href = url;
  a.download = row.filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}
</script>

<template>
  <div class="download-section-center">
    <re-pure-table
        ref="reTableRef"
        :data="pagedSamples"
        :columns="sample_columns"
        :row-key="(row:any) => String(row.UniqueID)"
        fit
        :pureTableMinWidth="600"
        :height="400"
        :show-pagination="true"
        @page-change="handleSamplePageChange"
        @page-size-change="handleSampleSizeChange"
        @select="onSelectRow"
        @select-all="onSelectAll"
        :pagination="{
        currentPage: sample_pagination.currentPage,
        pageSize: sample_pagination.pageSize,
        total: props.samples.length,
        layout: 'total, prev, pager, next, jumper'
      }"
    >
      <template #header>
        <div class="flex items-center gap-2">
              <span class="card-title text-blue-700 dark:text-blue-300 flex items-center">
                🧬 {{$t('Download_list')}}
              </span>
        </div>
      </template>
      <template #action="{ row }">
        <el-button type="primary" @click="editRow(row)">{{$t('Download_btn_download')}}</el-button>
      </template>
    </re-pure-table>
  </div>
</template>

<style scoped>
.download-section-center {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  width: 100%;
}
.table-card {
  width: 70%;
  margin-bottom: 24px;
  overflow-x: auto;
  border-radius: 18px;
  background: linear-gradient(90deg, #f6fff7 0%, #e3f2fd 100%);
  transition: background 0.3s, color 0.3s;
}
.dark .table-card {
  background: linear-gradient(90deg, #23272F 0%, #2E3440 100%);
  color: #F3F7FA;
}
.card-title {
  font-size: 1.3rem;
  font-weight: 700;
  letter-spacing: 1px;
  display: flex;
  align-items: center;
}
.table-scroll { width: 100%; overflow-x: auto; transition: background 0.3s, color 0.3s; }
.ellipsis-cell { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 180px; display: inline-block; }

.pagination-bar {
  display: flex;
  justify-content: center;
  padding: 16px 0 8px 0;
  background: transparent;
}
</style>