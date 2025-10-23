<script setup lang="ts">
import { ref, nextTick, defineExpose, computed, watch, onMounted, onBeforeUnmount } from 'vue';
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
  fullWidth?: boolean;

  autoColumnWidth?: boolean;
  autoColumnSampleSize?: number;
  minAutoColWidth?: number;
  maxAutoColWidth?: number;
  charPixel?: number;
  useCanvasMeasure?: boolean;
  cjkCharWeight?: number;

  expandToFit?: boolean;
  expandSkipTypes?: boolean;

  singleLine?: boolean;
  wrapCell?: boolean;

  cellAlign?: 'left' | 'center' | 'right';
  headerAlign?: 'left' | 'center' | 'right';

  selectionColWidth?: number;
  lockFirstDataCol?: boolean;   // 新增: 锁定勾选列后第一个数据列(默认 true)

  fit?: boolean;
  tableLayout?: 'auto' | 'fixed';
}>();

/* 默认值 */
const fit = computed(() => props.fit !== false);
const tableLayout = computed(() => props.tableLayout || 'auto');
const singleLine = computed(() => props.singleLine !== false);
const defaultCellAlign = computed(() => props.cellAlign || 'center');
const defaultHeaderAlign = computed(() => props.headerAlign || defaultCellAlign.value);
const lockFirstDataCol = computed(() => props.lockFirstDataCol !== false);

const layoutNoBuiltinsWithSlot = computed(() => {
  const base = props.pagination?.layout ?? 'prev, pager, next';
  const parts = base.split(',').map(s => s.trim()).filter(Boolean);
  const filtered = parts.filter(p => p !== 'total' && p !== 'jumper');
  if (!filtered.includes('slot')) filtered.unshift('slot');
  return filtered.join(', ');
});

const totalPages = computed(() => {
  const size = props.pagination?.pageSize || 10;
  const total = props.pagination?.total || 0;
  return Math.max(1, Math.ceil(total / size));
});

const jumpPage = ref<number>(props.pagination?.currentPage || 1);
watch(() => props.pagination?.currentPage, v => { if (typeof v === 'number' && v > 0) jumpPage.value = v; });
function onJump() {
  let p = Number(jumpPage.value) || 1;
  if (p < 1) p = 1;
  if (p > totalPages.value) p = totalPages.value;
  jumpPage.value = p;
  if (p !== props.pagination?.currentPage) emit('page-change', p);
}

const selectedRowKeys = defineModel<(string | number)[]>('selectedRowKeys', { default: () => [] });

const innerRef = ref<any>(null);
const scrollRef = ref<HTMLElement | null>(null);

/* Canvas 测量 */
let canvas: HTMLCanvasElement | null = null;
let ctx: CanvasRenderingContext2D | null = null;
function ensureCanvas() {
  if (canvas || props.useCanvasMeasure === false) return;
  canvas = document.createElement('canvas');
  ctx = canvas.getContext('2d');
  if (ctx) {
    const style = window.getComputedStyle(document.body);
    const font = `${style.fontWeight} ${style.fontSize} ${style.fontFamily}`;
    ctx.font = font;
  }
}
function measureTextPx(text: string): number {
  if (!text) return 0;
  ensureCanvas();
  if (ctx && props.useCanvasMeasure !== false) return ctx.measureText(text).width;
  const cjkWeight = props.cjkCharWeight ?? 2;
  let units = 0;
  for (const ch of text) {
    if (/[\u4e00-\u9fa5\u3400-\u4dbf\uF900-\uFAFF]/.test(ch)) units += cjkWeight;
    else if (/[\uFF00-\uFFEF]/.test(ch)) units += 1.5;
    else units += 1;
  }
  return units * (props.charPixel ?? 12);
}

/* 列处理 */
const processedColumns = ref<any[]>([]);
let baseAutoColumns: any[] = [];

function injectAlign(col: any) {
  if (col.align == null) col.align = defaultCellAlign.value;
  if (col.headerAlign == null) col.headerAlign = defaultHeaderAlign.value;
  return col;
}

function normalizeSelectionColumn(col: any) {
  const fixedW = props.selectionColWidth ?? 1;
  col.width = fixedW;
  col.minWidth = fixedW;
  col.maxWidth = fixedW;
  col.fixed = 'left';
  return col;
}

function buildBaseAutoColumns() {
  if (!props.columns?.length) {
    baseAutoColumns = [];
    processedColumns.value = [];
    return;
  }
  if (!props.autoColumnWidth) {
    baseAutoColumns = props.columns.map(raw => {
      const col = { ...raw };
      if (col.type === 'selection') normalizeSelectionColumn(col);
      return injectAlign(col);
    });
    processedColumns.value = [...baseAutoColumns];
    return;
  }
  const sampleSize = props.autoColumnSampleSize ?? 30;
  const minW = props.minAutoColWidth ?? 80;
  const maxW = props.maxAutoColWidth ?? 520;
  const sampleRows = props.data.slice(0, sampleSize);

  baseAutoColumns = props.columns.map(rawCol => {
    const col = { ...rawCol };
    if (col.type === 'selection') {
      normalizeSelectionColumn(col);
      return injectAlign(col);
    }
    if (col.width) return injectAlign(col);
    if (col.type && col.minWidth) return injectAlign(col);
    if (col.type && !col.minWidth && (col.type === 'index' || col.type === 'expand')) {
      col.minWidth = col.minWidth || 52;
      return injectAlign(col);
    }
    const header = String(col.label ?? col.prop ?? '');
    let maxPx = measureTextPx(header);
    if (col.prop) {
      for (const row of sampleRows) {
        const raw = row?.[col.prop];
        const text = raw == null ? '' : String(raw);
        const w = measureTextPx(text);
        if (w > maxPx) maxPx = w;
      }
    }
    const est = maxPx + 32;
    col.minWidth = Math.min(maxW, Math.max(minW, Math.ceil(est)));
    return injectAlign(col);
  });

  // selection 列置前
  const sel = baseAutoColumns.filter(c => c.type === 'selection');
  const others = baseAutoColumns.filter(c => c.type !== 'selection');
  baseAutoColumns = [...sel, ...others];

  processedColumns.value = [...baseAutoColumns];
}

function expandColumnsToFit(force = false) {
  if (!scrollRef.value || !baseAutoColumns.length) {
    processedColumns.value = [...baseAutoColumns];
    return;
  }
  if ((!props.expandToFit && !force)) {
    processedColumns.value = [...baseAutoColumns];
    return;
  }
  const containerWidth = scrollRef.value.clientWidth;
  if (containerWidth <= 0) {
    processedColumns.value = [...baseAutoColumns];
    return;
  }

  const result = baseAutoColumns.map(c => ({ ...c }));

  let canGrow = baseAutoColumns.filter(col => {
    if (col.width) return false;
    if (col.fixed) return false;
    if (props.expandSkipTypes !== false &&
        (col.type === 'selection' || col.type === 'index' || col.type === 'expand')) return false;
    return true;
  });

  // 勾选列后首个数据列锁定 (存在 selection 且满足数量)
  const hasSelection = baseAutoColumns.some(c => c.type === 'selection');
  let firstDataCol: any | null = null;
  if (hasSelection) {
    firstDataCol = baseAutoColumns.find(c => c.type !== 'selection');
    if (lockFirstDataCol.value && firstDataCol && canGrow.includes(firstDataCol) && canGrow.length > 1) {
      // 从可伸展集合中移除, 固定为 minWidth
      canGrow = canGrow.filter(c => c !== firstDataCol);
      const r = result.find(c => c === firstDataCol);
      if (r) r.width = r.minWidth;
    }
  }

  const totalMinGrow = canGrow.reduce((s, c) => s + (c.minWidth || 0), 0);
  const otherWidth = result
      .filter(c => !canGrow.includes(c))
      .reduce((s, c) => s + (c.width ? Number(c.width) : (c.minWidth || 0) || 0), 0);

  // 空数据按比例(或均值)填满
  if (props.data.length === 0 && canGrow.length) {
    const usable = Math.max(containerWidth - otherWidth, 0);
    const base = totalMinGrow || canGrow.length;
    canGrow.forEach(col => {
      const ratio = totalMinGrow ? (col.minWidth || 0) / base : 1 / canGrow.length;
      const target = Math.max(col.minWidth || 0, Math.floor(usable * ratio));
      const r = result.find(x => x === col);
      if (r) r.width = target;
    });
    processedColumns.value = result;
    return;
  }

  const gap = containerWidth - (totalMinGrow + otherWidth);
  if (gap <= 0) {
    processedColumns.value = result;
    return;
  }
  const ratioBase = totalMinGrow || 1;
  result.forEach(col => {
    if (!canGrow.includes(col)) return;
    const growRatio = (col.minWidth || 0) / ratioBase;
    const add = Math.floor(gap * growRatio);
    col.width = (col.minWidth || 0) + add;
  });

  processedColumns.value = result;
}

function recomputeAll() {
  buildBaseAutoColumns();
  nextTick(() => {
    expandColumnsToFit();
    requestAnimationFrame(() => expandColumnsToFit());
  });
}

/* 监听 */
watch(
    () => [props.columns, props.autoColumnWidth, props.cellAlign, props.headerAlign, props.selectionColWidth, props.lockFirstDataCol],
    () => recomputeAll(),
    { deep: true, immediate: true }
);
watch(() => props.data.length, () => recomputeAll());

/* ResizeObserver */
let ro: ResizeObserver | null = null;
onMounted(() => {
  if (scrollRef.value) {
    ro = new ResizeObserver(() => {
      requestAnimationFrame(() => expandColumnsToFit());
    });
    ro.observe(scrollRef.value);
  }
  nextTick(() => requestAnimationFrame(() => expandColumnsToFit(true)));
});
onBeforeUnmount(() => { ro && ro.disconnect(); });

/* 暴露实例方法 */
function getTableRef() {
  return innerRef.value?.getTableRef?.() ??
      innerRef.value?.elTableRef ??
      innerRef.value?.tableRef;
}
function clearSelection() { getTableRef()?.clearSelection?.(); }
function toggleRowSelection(row: any, selected = true) { getTableRef()?.toggleRowSelection?.(row, selected); }
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
    if (keySet.has(getKey(row))) el.toggleRowSelection(row, true);
  }
}

defineExpose({
  getTableRef,
  clearSelection,
  toggleRowSelection,
  syncSelectionByKeys
});
</script>

<template>
  <el-card
      class="table-card shadow-lg bg-white dark:bg-gray-900 dark:text-gray-100 transition-all border-none"
      shadow="hover"
      :class="[cardClass, { 'w-full': fullWidth }]"
  >
    <template #header>
      <slot name="header">
        <div class="flex items-center gap-2">
          <span v-if="title" :class="['card-title', titleClass]">{{ title }}</span>
          <slot name="header-extra" />
        </div>
      </slot>
    </template>

    <div
        ref="scrollRef"
        class="table-scroll bg-white dark:bg-gray-950 dark:text-gray-100 rounded-lg p-2 transition-all pure-table"
        :class="[
        scrollClass,
        singleLine ? 'is-ellipsis' : (wrapCell ? 'is-wrap' : 'is-ellipsis')
      ]"
        :style="{ width: '100%', overflowX: 'auto', overflowY: 'hidden' }"
    >

      <PureTable
          ref="innerRef"
          :data="data"
          :columns="processedColumns"
          :row-key="rowKey"
          empty-text=""
          :height="height"
          :fit="fit"
          :table-layout="tableLayout"
          v-bind="$attrs"
          v-model:selected-row-keys="selectedRowKeys"
          @select="(...args) => $emit('select', ...args)"
          @select-all="(...args) => $emit('select-all', ...args)"
          @selection-change="(...args) => $emit('selection-change', ...args)"
      >
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

<style scoped>
.table-card {
  width: 100%;
  margin-bottom: 24px;
  border-radius: 18px;
  overflow: visible;
  background: linear-gradient(90deg, #f6fff7 0%, #e3f2fd 100%);
  transition: background .3s, color .3s;
}
.dark .table-card {
  background: linear-gradient(90deg, #23272F 0%, #2E3440 100%);
  color: #F3F7FA;
}
.table-scroll {
  width: 100%;
  min-width: 0;
  box-sizing: border-box;
}
.table-scroll :deep(.el-table) {
  width: 100% !important;
}
.table-scroll.is-ellipsis :deep(th),
.table-scroll.is-ellipsis :deep(td) {
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
}
.table-scroll.is-wrap :deep(th),
.table-scroll.is-wrap :deep(td) {
  white-space: normal;
  word-break: break-word;
  line-height: 1.35;
}
.table-scroll :deep(th),
.table-scroll :deep(td) {
  text-align: center;
  vertical-align: middle;
}
.card-title {
  font-size: 1.1rem;
  font-weight: 600;
  display: flex;
  align-items: center;
}
.pagination-bar {
  display: flex;
  justify-content: center;
  padding: 16px 0 8px;
  background: transparent;
}


</style>