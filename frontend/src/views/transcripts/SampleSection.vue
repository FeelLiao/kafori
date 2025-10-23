<template>
  <section class="mb-16">
    <div class="rounded-2xl shadow-xl bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 p-8 mb-8">
      <div class="flex items-center gap-4 mb-6">
        <span class="text-xl font-bold text-blue-700 dark:text-blue-300 tracking-wide">🧬 {{$t('Transcripts_sample')}}</span>
      </div>

      <div class="flex flex-wrap items-center gap-4 mb-4">
        <!-- 组合排序控制面板 -->
        <div class="flex items-center gap-2">
          <el-select v-model="newSort.prop" :placeholder="$t('Transcripts_sel_col')" clearable size="small" style="width: 180px">
            <el-option
                v-for="opt in sortOptions"
                :key="opt.prop"
                :label="opt.label"
                :value="opt.prop"
            />
          </el-select>
          <el-select v-model="newSort.order" placeholder="方向" clearable size="small" style="width: 120px">
            <el-option :label="$t('Transcripts_asc')" value="asc" />
            <el-option :label="$t('Transcripts_desc')" value="desc" />
          </el-select>
          <el-button size="small" type="primary" @click="addSort" :disabled="!newSort.prop || !newSort.order">{{ $t('Transcripts_add_sort') }}</el-button>
        </div>

        <div class="ml-4">
          <template v-if="sortCriteria.length">
            <span v-for="(c, idx) in sortCriteria" :key="c.prop" class="inline-flex items-center gap-1 mr-2">
              <el-tag size="small">{{ idx + 1 }}. {{ columnLabel(c.prop) }} ({{ c.order === 'asc' ? '↑' : '↓' }})</el-tag>
              <el-button :icon="ArrowUp" size="mini" @click="moveUp(idx)" :disabled="idx===0" />
              <el-button :icon="ArrowDown" size="mini" @click="moveDown(idx)" :disabled="idx===sortCriteria.length-1" />
              <el-button :icon="Delete" size="mini" @click="removeSort(idx)" />
            </span>
            <el-button size="small" @click="clearSort">{{ $t('Transcripts_clear') }}</el-button>
          </template>
        </div>
      </div>



      <re-pure-table
          ref="reTableRef"
          :data="pagedSamples"
          :columns="sample_columns"
          :row-key="(row:any) => String(row.UniqueID)"
          :full-width="true"
          auto-column-width
          expand-to-fit
          fit
          :expand-skip-types="true"
          :min-auto-col-width="50"
          :max-auto-col-width="1000"
          :char-pixel="12"
          single-line
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
              🧬 {{$t('Transcripts_sample_list')}}
            </span>
<!--            <el-button type="primary" @click="">{{$t('Transcripts_search')}}</el-button>-->
          </div>
        </template>
        <template #SampleID="{ row }">
              <span :title="row.SampleID" class="ellipsis-cell dark:text-gray-100">
                {{ row.SampleID }}
              </span>
        </template>
        <template #SampleDetail="{ row }">
              <span :title="row.SampleDetail" class="ellipsis-cell dark:text-gray-100">
                {{ row.SampleDetail }}
              </span>
        </template>
        <template #Accession="{ row }">
              <span :title="row.Accession" class="ellipsis-cell dark:text-gray-100">
                {{ row.Accession }}
              </span>
        </template>
        <template #action="{ row }">
          <el-button type="primary" size="small" @click="editRow(row)">
            检索
          </el-button>
        </template>
      </re-pure-table>    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, watch, computed, nextTick } from 'vue';
import i18n from '@/i18n/index.ts'
import type { UploadInstance, UploadProps } from 'element-plus';
import RePureTable from '@/components/re-pure-table.vue';
import { getTranscriptType, transcript_analysis } from '@/api/index.ts';
import type { Sample } from '@/api/interface.ts';
import {ArrowDown, ArrowUp, Delete} from "@element-plus/icons-vue";

const props = defineProps<{
  samples: Sample[]
}>();
const emits = defineEmits<{
  (e: 'analyzed', payload: { res: any; width: number; height: number }): void
  (e: 'update:selectedSampleIds', ids: Array<string | number>): void
}>();

// 分页
const sample_pagination = ref({
  pageSize: 100,
  currentPage: 1,
  total: props.samples.length,
});

// 组合排序状态：数组顺序表示优先级（0 优先）
type SortCriterion = { prop: string; order: 'asc' | 'desc' };
const sortCriteria = ref<SortCriterion[]>([]);

// 新增排序临时数据（UI 用）
const newSort = ref<SortCriterion>({ prop: '', order: 'asc' });

// 从 columns 生成可排序选项
const sample_columns =  computed(() => [
  { type: 'selection'},
  { prop: 'SampleID', label: i18n.global.t('Transcripts_sample_id'), slot: 'SampleID', width: 120, sortable: true },
  { prop: 'SampleAge', label: i18n.global.t('Transcripts_sample_age'), sortable: true },
  { prop: 'SampleDetail', label: i18n.global.t('Transcripts_sample_detail'), slot: 'SampleDetail', width: 150, minWidth: 150, sortable: true },
  { prop: 'DepositDatabase', label: i18n.global.t('Transcripts_sample_db'), sortable: true },
  { prop: 'Accession', label: i18n.global.t('Transcripts_sample_acn'), slot: 'Accession', sortable: true },
  { prop: 'Origin', label: i18n.global.t('Transcripts_sample_origin'), sortable: true },
  { prop: 'CollectionPart', label: i18n.global.t('Transcripts_sample_cpt'), sortable: true },
  { prop: 'CollectionTime', label: i18n.global.t('Transcripts_sample_cte'), sortable: true },
]);

const sortOptions = computed(() =>
    sample_columns.value
        .filter(c => c.prop && c.sortable)
        .map(c => ({ prop: c.prop, label: (c as any).label || c.prop }))
);

// 添加排序准则（若已存在则更新顺序/方向）
function addSort() {
  const s = newSort.value;
  if (!s.prop || !s.order) return;
  const idx = sortCriteria.value.findIndex(x => x.prop === s.prop);
  if (idx >= 0) {
    // 更新并把移到末尾（最低优先）或保持原位，根据需求这里把新设置放到末尾（最低优先）
    sortCriteria.value.splice(idx, 1);
  }
  sortCriteria.value.push({ prop: s.prop, order: s.order });
  // 重置选择
  newSort.value = { prop: '', order: 'asc' };
}

function removeSort(idx: number) {
  sortCriteria.value.splice(idx, 1);
}

function moveUp(idx: number) {
  if (idx <= 0) return;
  const arr = sortCriteria.value;
  const tmp = arr[idx - 1];
  arr[idx - 1] = arr[idx];
  arr[idx] = tmp;
}

function moveDown(idx: number) {
  const arr = sortCriteria.value;
  if (idx >= arr.length - 1) return;
  const tmp = arr[idx + 1];
  arr[idx + 1] = arr[idx];
  arr[idx] = tmp;
}

function clearSort() {
  sortCriteria.value = [];
}

function columnLabel(prop: string) {
  const col = sample_columns.value.find(c => c.prop === prop);
  return (col && (col as any).label) || prop;
}

// 多列比较器
function compareByCriteria(a: any, b: any) {
  for (const crit of sortCriteria.value) {
    const v1 = a[crit.prop];
    const v2 = b[crit.prop];
    if (v1 == null && v2 == null) continue;
    if (v1 == null) return crit.order === 'asc' ? -1 : 1;
    if (v2 == null) return crit.order === 'asc' ? 1 : -1;

    // 尝试数字比较
    const n1 = Number(v1);
    const n2 = Number(v2);
    let cmp = 0;
    if (!isNaN(n1) && !isNaN(n2)) {
      cmp = n1 < n2 ? -1 : n1 > n2 ? 1 : 0;
    } else {
      // 字符串比较（本地化可按需替换）
      cmp = String(v1).localeCompare(String(v2));
    }
    if (cmp !== 0) return crit.order === 'asc' ? cmp : -cmp;
  }
  return 0;
}

// 在渲染/分页前对原始数据进行排序
const sortedSamples = computed(() => {
  if (!sortCriteria.value.length) return props.samples.slice();
  const arr = props.samples.slice();
  arr.sort(compareByCriteria);
  return arr;
});

// 分页基于排序后的数组
const pagedSamples = computed(() => {
  const start = (sample_pagination.value.currentPage - 1) * sample_pagination.value.pageSize;
  const end = start + sample_pagination.value.pageSize;
  return sortedSamples.value.slice(start, end);
});

// 下面是原有的分页/选择/上传/分析等逻辑（保持不变）
// ...（保持原有代码）...

// 为保持响应式与编辑体验，将下面原有的函数和变量保留（在实际文件中请保留其余全部原实现）
const handleSamplePageChange = (page) => {
  sample_pagination.value.currentPage = page;
};
const handleSampleSizeChange = (size) => {
  sample_pagination.value.pageSize = size;
  sample_pagination.value.currentPage = 1;
};

const selectedSampleIds = ref<Array<string | number>>([]);
const reTableRef = ref<any>();
const syncingSelection = ref(false);



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
  emits('update:selectedSampleIds', selectedSampleIds.value);
}

function onSelectAll(selection: Sample[]) {
  if (syncingSelection.value) return;
  const pageIds = pagedSamples.value.map(r => String(r.UniqueID));
  if (selection.length) {
    const set = new Set([...selectedSampleIds.value, ...pageIds]);
    selectedSampleIds.value = Array.from(set);
  } else {
    selectedSampleIds.value = selectedSampleIds.value.filter(id => !pageIds.includes(id));
  }
  emits('update:selectedSampleIds', selectedSampleIds.value);
}

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

function editRow(row: Sample) {
  console.log('检索行', row);
}


</script>

<style scoped>
.table-card {
  width: 100%;
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

/* 保持通用省略类 */
.ellipsis-cell {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  box-sizing: border-box;
}

/* 针对 SampleDetail 的固定宽度（与列 width 保持一致） */
.ellipsis-cell-fixed {
  display: block;
  width: 150px;       /* 与 columns 中的 width 一致，可调整 */
  max-width: 150px;
  vertical-align: middle;
}
</style>