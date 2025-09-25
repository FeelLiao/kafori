<template>
  <el-card
      class="table-card shadow-lg bg-white dark:bg-gray-900 dark:text-gray-100 transition-all border-none"
      shadow="hover"
      :class="cardClass"
  >
    <template #header>
      <slot name="header">
        <div class="flex items-center gap-2">
          <span class="card-title flex items-center" :class="titleClass">
            {{ title }}
          </span>
          <div class="ml-auto flex items-center gap-2">
            <slot name="header-right" />
          </div>
        </div>
      </slot>
    </template>

    <div
        class="table-scroll bg-white dark:bg-gray-950 dark:text-gray-100 rounded-lg p-2 transition-all pure-table"
        :class="scrollClass"
        :style="{
        minWidth: pureTableMinWidth ? (typeof pureTableMinWidth === 'number' ? pureTableMinWidth + 'px' : pureTableMinWidth) : '1000px',
        maxWidth: '1700px'
      }"
    >
      <PureTable
          ref="innerRef"
          :data="data"
          :columns="columns"
          :row-key="rowKey"
          empty-text=""
          min-width="1000px"
          :height="height"
          v-bind="$attrs"
          v-model:selected-row-keys="selectedRowKeys"
          @select="(...args) => $emit('select', ...args)"
          @select-all="(...args) => $emit('select-all', ...args)"
          @selection-change="(...args) => $emit('selection-change', ...args)"
      >
        <!-- 透传所有具名插槽到内部表格 -->
        <template v-for="(_, name) in $slots" #[name]="slotProps">
          <slot :name="name" v-bind="slotProps" />
        </template>
      </PureTable>
    </div>

    <!-- 可选分页 -->
    <div v-if="showPagination" class="pagination-bar">
      <el-pagination
          class="mt-4"
          background
          :current-page="pagination?.currentPage"
          :page-size="pagination?.pageSize"
          :total="pagination?.total || 0"
          :layout="layoutNoBuiltinsWithSlot"
          @current-change="(p:number) => $emit('page-change', p)"
          @size-change="(s:number) => $emit('page-size-change', s)"
      >
        <!-- 默认插槽：需要在 layout 中包含 'slot' 才会显示 -->
        <template #default>
          <!-- 父组件可用 #pagination 覆写 -->
          <slot name="pagination">
            <span style="margin-right:12px;">{{$t('Transcripts_total')}} {{ pagination?.total || 0 }} </span>
            <span style="display:inline-flex;align-items:center;gap:8px;">
              <span>{{$t('Transcripts_jump')}}</span>
              <el-input
                  type="number"
                  :min="1"
                  :max="totalPages"
                  v-model.number="jumpPage"
                  @keyup.enter="onJump"
                  @blur="onJump"
                  style="width:72px;padding:4px 6px;"
              />
              <span>{{$t('Transcripts_page')}}</span>
            </span>
          </slot>
        </template>
      </el-pagination>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, nextTick, defineExpose, computed, watch } from 'vue';
import { PureTable } from '@pureadmin/table';

const emit = defineEmits([
  'select',
  'select-all',
  'selection-change',
  'page-change',
  'page-size-change'
]);

const props = defineProps<{
  title?: string;
  titleClass?: string | string[];
  data: any[];
  columns: any[];
  pureTableMinWidth?: string | number;
  height?: number | string;
  rowKey?: string | ((row: any) => string | number);
  showPagination?: boolean;
  pagination?: {
    currentPage: number;
    pageSize: number;
    total: number;
    layout?: string;
  };
  cardClass?: string | string[];
  scrollClass?: string | string[];
  gotoText?: string;            // 自定义“跳至”
  pageClassifierText?: string;  // 自定义“页”
}>();

// 计算 layout：移除 total 与 jumper，确保包含 slot
const layoutNoBuiltinsWithSlot = computed(() => {
  const base = props.pagination?.layout ?? 'prev, pager, next';
  const parts = base.split(',').map(s => s.trim()).filter(Boolean);
  const filtered = parts.filter(p => p !== 'total' && p !== 'jumper');
  if (!filtered.includes('slot')) filtered.unshift('slot');
  return filtered.join(', ');
});

// 自定义“跳至 / 页”文案

// 计算总页数与跳转逻辑
const totalPages = computed(() => {
  const size = props.pagination?.pageSize || 10;
  const total = props.pagination?.total || 0;
  return Math.max(1, Math.ceil(total / size));
});

const jumpPage = ref<number>(props.pagination?.currentPage || 1);
watch(
    () => props.pagination?.currentPage,
    v => { if (typeof v === 'number' && v > 0) jumpPage.value = v; }
);

function onJump() {
  let p = Number(jumpPage.value) || 1;
  if (p < 1) p = 1;
  if (p > totalPages.value) p = totalPages.value;
  // 回写输入框为合法页码
  jumpPage.value = p;
  // 通知父组件更新 currentPage
  if (p !== props.pagination?.currentPage) emit('page-change', p);
}

// 对外暴露的 v-model：selected-row-keys
const selectedRowKeys = defineModel<(string | number)[]>('selectedRowKeys', {
  default: () => []
});

const innerRef = ref<any>(null);

// 获取内部 el-table 引用
function getTableRef() {
  return (
      innerRef.value?.getTableRef?.() ??
      innerRef.value?.elTableRef ??
      innerRef.value?.tableRef
  );
}

// 清空/切换行选择
function clearSelection() {
  const el = getTableRef();
  el?.clearSelection?.();
}
function toggleRowSelection(row: any, selected = true) {
  const el = getTableRef();
  el?.toggleRowSelection?.(row, selected);
}

// 根据 keys 回显选择
async function syncSelectionByKeys(keys: Array<string | number>) {
  const el = getTableRef();
  if (!el?.clearSelection || !el?.toggleRowSelection) return;

  await nextTick();
  el.clearSelection();

  const toKeyStr = (k: any) => String(k);
  const keySet = new Set(keys.map(toKeyStr));
  const getKey =
      typeof props.rowKey === 'function'
          ? (row: any) => toKeyStr((props.rowKey as Function)(row))
          : (row: any) => toKeyStr(row[props.rowKey || 'id']);

  for (const row of props.data || []) {
    if (keySet.has(getKey(row))) {
      el.toggleRowSelection(row, true);
    }
  }
}

defineExpose({
  getTableRef,
  clearSelection,
  toggleRowSelection,
  syncSelectionByKeys
});
</script>

<style scoped>
.table-card {
  min-width: 1200px;
  max-width: 1800px;
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

:deep(.pure-table th),
:deep(.pure-table td) {
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
  text-align: center !important;
  vertical-align: middle !important;
}

.card-title {
  font-size: 1.3rem;
  font-weight: 700;
  letter-spacing: 1px;
  display: flex;
  align-items: center;
}
.table-scroll { width: 100%; overflow-x: auto; transition: background 0.3s, color 0.3s; }
.pagination-bar { display: flex; justify-content: center; padding: 16px 0 8px 0; background: transparent; }
</style>