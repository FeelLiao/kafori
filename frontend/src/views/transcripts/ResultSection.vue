<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import JSZip from 'jszip';
import RePureTable from '@/components/re-pure-table.vue';
import { getTranscriptType, transcript_analysis } from "@/api";
import type { UploadInstance, UploadProps } from "element-plus";

const props = defineProps<{
  res: any;
  width: number;
  height: number;
  selectedSampleIds: Array<string | number>;
}>();

const emits = defineEmits<{
  (e: 'analyzed', payload: { res: any; width: number; height: number }): void
}>();

const tables = computed(() => props.res?.tables || {});
const selectedSampleIds = ref<Array<string | number>>(props.selectedSampleIds ?? []);
watch(
    () => props.selectedSampleIds,
    (ids) => {
      selectedSampleIds.value = ids ?? [];
    },
    { immediate: true }
);

// 控制前端展示尺寸：不直接使用传入的大尺寸，限制一个最大显示宽度
const displaySize = computed(() => {
  // 限制最大显示宽度（可根据需要调整 360 为其他值）
  const maxDisplay = Math.min(props.width ?? 900, 360);
  const w = Math.max(160, Math.round(maxDisplay)); // 最小保持 160 防止太小
  const h = Math.round(w * 2 / 3); // 3:2 比例
  return { w, h };
});

function getColumns(data: any[]) {
  if (!data || !data.length) return [];
  return Object.keys(data[0]).map(key => ({
    prop: key,
    label: key
  }));
}

function genCSV(data: any[]) {
  if (!data.length) return '';
  const columns = getColumns(data);
  const headers = columns.map(col => col.label);
  const keys = columns.map(col => col.prop);
  const rows = data.map(row => keys.map(k => row[k]));
  return [headers, ...rows]
      .map(r => r.map(v => `"${String(v ?? '')}"`).join(','))
      .join('\r\n');
}

async function exportAllCSV() {
  const zip = new JSZip();
  for (const tableKey in tables.value) {
    const data = tables.value[tableKey];
    if (data && data.length) {
      zip.file(`${tableKey}.csv`, genCSV(data));
    }
  }
  const blob = await zip.generateAsync({ type: 'blob' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'all_tables.zip';
  a.click();
  URL.revokeObjectURL(url);
}

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

const GeneId_textarea = ref('');
const parsedGenIdList_f = ref<string[]>([]);
const ParaseGenIdList = ref<string[]>([]);
const radio = ref<'1' | '2' | '3'>('1');
const transcript_type = ref<any[]>([]);
const transcript_type_value = ref('');
const width = ref(900);
const height = ref(600);

async function fetch_transcript_type() {
  transcript_type.value = await getTranscriptType();
}
fetch_transcript_type();

function parse_geneid(text: string): string[] {
  return text.split('\n').map(s => s.trim()).filter(Boolean);
}

const upload = ref<UploadInstance>();
const handleUpload: UploadProps['onChange'] = (file) => {
  const rawFile = file.raw;
  if (!rawFile) return;
  const reader = new FileReader();
  reader.onload = (e) => {
    const text = e.target?.result as string;
    parsedGenIdList_f.value = parse_geneid(text);
  };
  reader.readAsText(rawFile);
};

async function submit_transcirpt() {
  let res: any;
  if (radio.value === '1') {
    ParaseGenIdList.value = parse_geneid(GeneId_textarea.value);
    res = await transcript_analysis(
        transcript_type_value.value,
        width.value,
        height.value,
        selectedSampleIds.value,
        ParaseGenIdList.value,
        false
    );
  } else if (radio.value === '2') {
    res = await transcript_analysis(
        transcript_type_value.value,
        width.value,
        height.value,
        selectedSampleIds.value,
        parsedGenIdList_f.value,
        false
    );
  } else {
    res = await transcript_analysis(
        transcript_type_value.value,
        width.value,
        height.value,
        selectedSampleIds.value,
        [],
        true
    );
  }
  emits('analyzed', { res, width: width.value, height: height.value });
}

// 一键打包所有图片为 zip
async function exportAllImagesZip() {
  const plots = props.res?.plots || [];
  if (!plots.length) return;
  const zip = new JSZip();
  for (let i = 0; i < plots.length; i++) {
    const plot = plots[i];
    const dataUrl = `data:${plot.format},${plot.data}`;
    try {
      const resp = await fetch(dataUrl);
      const blob = await resp.blob();
      const safeTitle = (plot.title || `plot_${i+1}`).replace(/[\\\/:*?"<>|]+/g, '_');
      const filename = `${safeTitle}.svg`;
      zip.file(filename, blob);
    } catch (e) {
      console.warn('export image failed', plot, e);
    }
  }
  const blobZip = await zip.generateAsync({ type: 'blob' });
  const url = URL.createObjectURL(blobZip);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'plots_images.zip';
  a.click();
  URL.revokeObjectURL(url);
}

// 监听变化并输出
watch(transcript_type_value, (newVal, oldVal) => {
  console.log('transcript_type_value 变化:', newVal);
});
</script>

<template>
  <section class="mb-16">
    <div class="rounded-2xl shadow-xl bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 p-8 mb-8">
      <div class="flex items-center gap-4 mb-6">
        <span class="text-xl font-bold text-blue-700 dark:text-blue-300 tracking-wide">📊 {{$t('Transcripts_analysis')}}</span>
      </div>

      <div class="flex flex-row gap-4 mb-4 items-center">
        <el-select v-model="transcript_type_value" :placeholder="$t('Transcripts_Analysis_Type')" style="width: 180px" class="ml-0">
          <el-option v-for="item in transcript_type" :key="item.id" :label="item.title" :value="item.id" />
        </el-select>
        <el-button type="success" @click="submit_transcirpt" class="ml-0">{{$t('Transcripts_analysis')}}</el-button>
      </div>
      <div
          v-if="transcript_type_value === 'pca'"
          class="param-box mb-8"
      >
        <div class="flex flex-wrap items-center gap-4">
          <el-input
              v-model="GeneId_textarea"
              style="width: 240px;"
              :autosize="{ minRows: 2, maxRows: 2 }"
              type="textarea"
              placeholder="Gene ID / Name"
              class="ml-0"
          />
          <el-upload
              ref="upload"
              class="upload-demo ml-0"
              :limit="1"
              :on-change="handleUpload"
              :auto-upload="false"
          >
            <template #trigger>
              <el-button type="primary">{{$t('Transcripts_upload')}}</el-button>
            </template>
          </el-upload>
          <el-radio-group v-model="radio" class="ml-0">
            <el-radio value="1" size="large">{{ $t('Transcripts_option1') }}</el-radio>
            <el-radio value="2" size="large">{{ $t('Transcripts_option2') }}</el-radio>
            <el-radio value="3" size="large">{{ $t('Transcripts_option3') }}</el-radio>
          </el-radio-group>
          <el-input-number v-model="width" :min="1" :max="1000" class="ml-0" />
          <el-input-number v-model="height" :min="1" :max="1000" class="ml-2" />
        </div>
      </div>

      <div v-if="Object.keys(tables).length" class="flex mb-4">
        <el-button type="primary" @click="exportAllImagesZip" class="export-btn">{{ $t('Transcripts_down_images') }}</el-button>
      </div>

      <div class="plots-grid">
        <div
            v-for="(plot, idx) in (res?.plots || [])"
            :key="plot.title + '_' + idx"
            class="plot-block"
        >
          <div class="font-bold text-base mb-3 text-green-700 dark:text-green-300 flex items-center">
            <span class="mr-2"></span>{{ plot.title }}
          </div>
          <el-image
              :src="`data:${plot.format},${plot.data}`"
              fit="contain"
              class="plot-image transition-all duration-300 hover:shadow-xl"
              :style="{ maxWidth: displaySize.w + 'px', height: displaySize.h + 'px' }"
          />
        </div>
      </div>

      <div v-if="Object.keys(tables).length" class="flex flex-row gap-4 mb-8 items-center">
        <el-button type="primary" @click="exportAllCSV" class="export-btn">
          {{ $t('Transcripts_down_csv') }}
        </el-button>
      </div>

      <div class="flex flex-row flex-wrap gap-4 mb-8">
        <div
            v-for="(tableData, tableKey) in tables"
            :key="tableKey"
            class="export-block flex flex-col items-start p-4 rounded-lg bg-gray-50 dark:bg-gray-800 shadow"
        >
          <div class="font-bold text-lg mb-2 text-gray-700 dark:text-gray-200">{{ tableKey }}</div>
          <el-button type="success" @click="exportCSV(tableKey)" class="export-btn">
            {{ tableKey }} CSV
          </el-button>
        </div>
      </div>

    </div>
  </section>
</template>

<style scoped>
.plots-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 24px;
  justify-items: center;
  align-items: start;
  margin-bottom: 24px;
}
.plot-block {
  border-radius: 12px;
  padding: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  width: 100%;
  max-width: 420px;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.plot-image {
  width: 100%;
  /* 使用高度配合 displaySize 保证 3:2 */
  object-fit: contain;
  border-radius: 10px;
  border: 1px solid #eaeaea;
  background: #fff;
}
/* 其余样式保持 */
.export-block {
  min-width: 220px;
  max-width: 320px;
  margin-bottom: 0;
}
.export-btn {
  margin-right: 0;
  margin-bottom: 8px;
  border-radius: 8px;
  font-weight: 500;
  letter-spacing: 1px;
  box-shadow: 0 2px 8px #e0e7ef33;
  transition: box-shadow 0.2s;
}
.export-btn:hover {
  box-shadow: 0 4px 16px #90caf933;
}

.param-box {
  border: 1.5px solid #eaeaea;
  border-radius: 16px;
  background: #f9fafb;
  box-shadow: 0 2px 12px #e0e7ef33;
  padding: 20px;
  transition: background 0.3s, border 0.3s;
}
.dark .param-box {
  background: #23272e;
  border-color: #444c56;
  box-shadow: 0 2px 12px #23272e55;
}
</style>