<template>
  <section ref="experimentSection" class="mb-16">
    <div class="rounded-2xl shadow-xl bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 p-8 mb-8">
      <div class="flex items-center gap-4 mb-6">
        <span class="text-xl font-bold text-green-700 dark:text-green-300 tracking-wide">🧪 {{$t('Transcripts_experiment')}}</span>
      </div>
      <div class="flex items-center gap-4 mb-8">
        <el-select
            v-model="categoryValue"
            multiple
            clearable
            collapse-tags
            :placeholder="`🔎 ${$t('Transcripts_exp_category')}`"
            popper-class="custom-header"
            :max-collapse-tags="1"
            style="width: 240px"
            class="mr-2"
        >
          <template #header>
            <el-checkbox
                v-model="checkAll"
                :indeterminate="indeterminate"
                @change="handleCheckAll"
            >
              All
            </el-checkbox>
          </template>
          <el-option
              v-for="item in expData"
              :key="item.ExpClass"
              :label="item.ExperimentCategory"
              :value="item.ExpClass"
          />
        </el-select>
        <el-button type="primary" @click="searchExperiments" class="ml-2">{{$t('Transcripts_search')}}</el-button>
      </div>

      <re-pure-table
          ref="reTableRef"
          :data="pagedExperiments"
          :columns="columns"
          :row-key="(row:any) => String(row.UniqueEXID)"
          :full-width="true"
          auto-column-width
          expand-to-fit
          fit
          :expand-skip-types="true"
          :min-auto-col-width="parentWidth"
          :max-auto-col-width="480"
          :char-pixel="12"
          single-line
          :height="400"
          :show-pagination="true"
          @select="onSelectRow"
          @select-all="onSelectAll"
          @page-change="handleExperimentPageChange"
          @page-size-change="handleExperimentSizeChange"
          :pagination="{
      currentPage: experiment_pagination.currentPage,
      pageSize: experiment_pagination.pageSize,
      total: experimentData.length,
      layout: 'total, prev, pager, next, jumper'
    }"
      >
        <template #header>
          <div class="flex items-center gap-2">
        <span class="card-title text-blue-700 dark:text-blue-300 flex items-center">
          🧪 {{$t('Transcripts_experiment_list')}}
        </span>
            <el-button type="primary" @click="emitFetchSamples">
              {{$t('Transcripts_search')}}
            </el-button>
          </div>
        </template>

        <template #experimentCategory="{ row }">
      <span :title="getExpCategory(row.ExpClass)" class="ellipsis-cell dark:text-gray-100">
        {{ getExpCategory(row.ExpClass) }}
      </span>
        </template>

        <template #experiment="{ row }">
      <span :title="row.Experiment" class="ellipsis-cell dark:text-gray-100">
        {{ row.Experiment }}
      </span>
        </template>

        <template #action="{ row }">
          <el-button type="primary" size="small" @click="emitFetchSamples">
            检索
          </el-button>
        </template>
      </re-pure-table>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, watch, computed, nextTick, onMounted } from 'vue';
import i18n from '@/i18n/index.ts'
import RePureTable from '@/components/re-pure-table.vue';
import type { CheckboxValueType } from 'element-plus';
import { transcriptsQuery } from '@/api/index.ts';
import type { ExpClassDTO, Experiment } from '@/api/interface.ts';

const emits = defineEmits<{
  (e: 'update:selectedExperimentIds', ids: Array<string | number>): void
  (e: 'fetch-samples'): void
}>();

// 分类与实验数据
const checkAll = ref(false);
const indeterminate = ref(false);
const categoryValue = ref<CheckboxValueType[]>([]);

const expData = ref<ExpClassDTO[]>([]);
const experimentData = ref<Experiment[]>([]);

const parentWidth = computed(() => {
  return document.querySelector('.table-card')?.clientWidth ?? 200;
});

async function fetchExpData() {
  expData.value = await transcriptsQuery('exp_class');
}
fetchExpData();

watch(categoryValue, (val) => {
  if (val.length === 0) {
    checkAll.value = false;
    indeterminate.value = false;
  } else if (val.length === expData.value.length) {
    checkAll.value = true;
    indeterminate.value = false;
  } else {
    indeterminate.value = true;
  }
});

function handleCheckAll(val: CheckboxValueType) {
  indeterminate.value = false;
  if (val) {
    categoryValue.value = expData.value.map((_) => _.ExpClass);
  } else {
    categoryValue.value = [];
  }
}

async function searchExperiments() {
  experimentData.value = await transcriptsQuery('exp_name', categoryValue.value);
  // 数据变更后重置分页到第 1 页
  experiment_pagination.value.currentPage = 1;
}

// 分页
const experiment_pagination = ref({
  pageSize: 100,
  currentPage: 1
});
const pagedExperiments = computed(() => {
  const start = (experiment_pagination.value.currentPage - 1) * experiment_pagination.value.pageSize;
  const end = start + experiment_pagination.value.pageSize;
  return experimentData.value.slice(start, end);
});
function handleExperimentPageChange(page: number) {
  experiment_pagination.value.currentPage = page;
}
function handleExperimentSizeChange(size: number) {
  experiment_pagination.value.pageSize = size;
  experiment_pagination.value.currentPage = 1;
}

// 全局多选（跨页）
const selectedExperimentIds = ref<string[]>([]);
const reTableRef = ref<any>();
const syncingSelection = ref(false);

// 单行选择/取消（增量维护全局）
function onSelectRow(selection: Experiment[], row: Experiment) {
  if (syncingSelection.value) return;
  const id = String(row.UniqueEXID);
  const checked = selection.some(r => String(r.UniqueEXID) === id);
  if (checked) {
    if (!selectedExperimentIds.value.includes(id)) {
      selectedExperimentIds.value = [...selectedExperimentIds.value, id];
    }
  } else {
    selectedExperimentIds.value = selectedExperimentIds.value.filter(x => x !== id);
  }
  emits('update:selectedExperimentIds', selectedExperimentIds.value);
}

// 本页全选/全不选
function onSelectAll(selection: Experiment[]) {
  if (syncingSelection.value) return;
  const pageIds = pagedExperiments.value.map(r => String(r.UniqueEXID));
  if (selection.length) {
    const set = new Set([...selectedExperimentIds.value, ...pageIds]);
    selectedExperimentIds.value = Array.from(set);
  } else {
    selectedExperimentIds.value = selectedExperimentIds.value.filter(id => !pageIds.includes(id));
  }
  emits('update:selectedExperimentIds', selectedExperimentIds.value);
}

// 数据或分页变化时，对当前页按全局 keys 回显
watch(
    () => [pagedExperiments.value, selectedExperimentIds.value] as const,
    async () => {
      await nextTick();
      const table = reTableRef.value;
      if (!table?.syncSelectionByKeys) return;
      syncingSelection.value = true;
      try {
        await table.syncSelectionByKeys(selectedExperimentIds.value);
      } finally {
        await nextTick();
        syncingSelection.value = false;
      }
    },
    { deep: true }
);

// 其它
function emitFetchSamples() {
  emits('fetch-samples');
}
function getExpCategory(expClass: string) {
  const found = expData.value.find(item => item.ExpClass === expClass);
  return found ? found.ExperimentCategory : '-';
}

const columns = computed(() => [
  { type: 'selection' },
  { prop: 'UniqueEXID', label: i18n.global.t('Transcripts_exp_id'),width: 20},
  { prop: 'ExperimentCategory', label: i18n.global.t('Transcripts_exp_category'), slot: 'experimentCategory' },
  { prop: 'Experiment', label: i18n.global.t('Transcripts_exp_name'), slot: 'experiment' },
  { prop: 'action', label: i18n.global.t('Transcripts_exp_action'), slot: 'action' }
]);
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
</style>