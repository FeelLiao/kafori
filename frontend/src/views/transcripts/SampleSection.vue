<template>
  <section class="mb-16">
    <div class="rounded-2xl shadow-xl bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 p-8 mb-8">
      <div class="flex items-center gap-4 mb-6">
        <span class="text-xl font-bold text-blue-700 dark:text-blue-300 tracking-wide">🧬 {{$t('Transcripts_sample')}}</span>
      </div>

      <div class="flex flex-wrap items-center gap-4 mb-8">
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
          <el-radio value="1" size="large">Option 1</el-radio>
          <el-radio value="2" size="large">Option 2</el-radio>
          <el-radio value="3" size="large">Option 3</el-radio>
        </el-radio-group>
        <el-input-number v-model="width" :min="1" :max="1000" class="ml-0" />
        <el-input-number v-model="height" :min="1" :max="1000" class="ml-2" />
        <el-select v-model="transcript_type_value" placeholder="Transcript Type" style="width: 180px" class="ml-0">
          <el-option v-for="item in transcript_type" :key="item.id" :label="item.title" :value="item.id" />
        </el-select>
        <el-button type="success" @click="submit_transcirpt" class="ml-0">{{$t('Transcripts_analysis')}}</el-button>
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
            <el-button type="primary" @click="">{{$t('Transcripts_search')}}</el-button>
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

const props = defineProps<{
  samples: Sample[]
}>();
const emits = defineEmits<{
  (e: 'analyzed', payload: { res: any; width: number; height: number }): void
}>();

// 分页
const sample_pagination = ref({
  pageSize: 100,
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
const sample_columns =  computed(() => [
  { type: 'selection' },
  { prop: 'UniqueEXID', label: i18n.global.t('Transcripts_exp_id'),width: 10 },
  { prop: 'SampleID', label: i18n.global.t('Transcripts_sample_id'), slot: 'SampleID' },
  { prop: 'SampleAge', label: i18n.global.t('Transcripts_sample_age') },
  { prop: 'SampleDetail', label: i18n.global.t('Transcripts_sample_detail'), slot: 'SampleDetail' },
  { prop: 'DepositDatabase', label: i18n.global.t('Transcripts_sample_db') },
  { prop: 'Accession', label: i18n.global.t('Transcripts_sample_acn'), slot: 'Accession' },
  { prop: 'Origin', label: i18n.global.t('Transcripts_sample_origin') },
  { prop: 'CollectionPart', label: i18n.global.t('Transcripts_sample_cpt') },
  { prop: 'CollectionTime', label: i18n.global.t('Transcripts_sample_cte') },
  { prop: 'action', label: i18n.global.t('Transcripts_sample_action'), slot: 'action' }
]);

function editRow(row: Sample) {
  console.log('检索行', row);
}

// 分析参数/操作
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
</style>