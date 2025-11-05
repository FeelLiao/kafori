<template>
  <div class="p-6 space-y-6 text-gray-900 dark:text-gray-100">

    <!-- A1 样本文件上传 -->
    <el-card class="rounded-xl shadow-md border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900">
      <template #header>
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <span class="text-base font-semibold">A1｜{{$t('Pipelines_sample_upload')}}</span>
            <el-tag
                :type="is_uploadedA1 ? 'success' : 'info'"
                effect="dark"
                round
            >
              {{ is_uploadedA1 ? $t('Pipelines_uploaded') : $t('Pipelines_pending_upload') }}
            </el-tag>
          </div>
          <div class="text-xs text-gray-500 dark:text-gray-400">
            {{$t('Pipelines_A1_desc')}}
          </div>
        </div>
      </template>

      <div class="grid grid-cols-1 gap-4">
        <el-upload
            drag
            action="#"
            :file-list="fileListA1"
            :on-change="onFileChangeA1"
            :on-remove="onFileRemoveA1"
            :auto-upload="false"
            :limit="1"
            :show-file-list="true"
            accept=".csv,.tsv,.xlsx,.xls,.json"
            class="w-full"
        >
          <div class="el-upload__text">
            {{$t('Pipelines_drag_upload')}} <em>{{$t('Pipelines_click_upload')}}</em>
          </div>
          <template #tip>
            <div class="text-xs text-gray-500 dark:text-gray-400 mt-2">
              {{$t('Pipelines_A1_file_desc')}}
              <el-button
                  type="primary"
                  @click="uploadFileA1"
                  :loading="uploadingA1"
              >
                {{$t('Pipelines_upload')}}
              </el-button>
            </div>
          </template>
        </el-upload>

      </div>
    </el-card>

    <!-- 分割线 -->
    <el-divider class="!my-2">
      <span class="text-sm text-gray-500 dark:text-gray-400">{{$t('Pipelines_A1_tip')}}</span>
    </el-divider>

    <!-- A2 / A3 容器：默认以“未解锁”样式展示 -->
    <div class="grid grid-cols-1 xl:grid-cols-2 gap-6">
      <!-- A2：tpm / counts 上传路径 -->
      <div class="relative">
        <!-- 未解锁遮罩（仅视觉，实际逻辑后续接入） -->
<!--        <div class="absolute inset-0 rounded-xl bg-gradient-to-b from-white/60 to-white/30 dark:from-gray-900/60 dark:to-gray-900/30 backdrop-blur-[2px] border border-dashed border-gray-300 dark:border-gray-700 flex items-center justify-center z-10">-->
<!--          <div class="flex items-center gap-2">-->
<!--            <el-tag type="info" effect="dark" round>未解锁</el-tag>-->
<!--            <span class="text-sm text-gray-600 dark:text-gray-300">完成 A1 后可用</span>-->
<!--          </div>-->
<!--        </div>-->

        <el-card class="rounded-xl shadow-md border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900">
          <template #header>
            <div class="flex items-center justify-between">
              <span class="text-base font-semibold">A2｜{{$t('Pipelines_tpm_counts_upload')}}</span>
              <div class="flex items-center gap-2">
                <el-tag
                    :type="is_uploadedA2_1 ? 'success' : 'info'"
                    effect="dark"
                    round
                >
                  {{ is_uploadedA2_1 ? $t('Pipelines_tpm_uploaded') : $t('Pipelines_tpm_pending_upload') }}
                </el-tag>
                <el-tag
                    :type="is_uploadedA2_2 ? 'success' : 'info'"
                    effect="dark"
                    round
                >
                  {{ is_uploadedA2_2 ? $t('Pipelines_counts_uploaded') : $t('Pipelines_counts_pending_upload') }}
                </el-tag>

              </div>
            </div>
          </template>

          <div class="space-y-5">
            <div>
              <div class="mb-2 text-sm font-medium">tpm</div>
              <el-upload
                  drag
                  action="#"
                  :file-list="fileListA2_1"
                  :on-change="onFileChangeA2_1"
                  :on-remove="onFileRemoveA2_1"
                  :auto-upload="false"
                  :limit="1"
                  :show-file-list="true"
                  accept=".csv,.tsv,.xlsx,.xls,.mtx,.txt,.json"
                  class="w-full"
              >
                <div class="el-upload__text">
                  {{$t('Pipelines_drag_upload')}} <em>{{$t('Pipelines_click_upload')}}</em>
                </div>
              </el-upload>
            </div>

            <div>
              <div class="mb-2 text-sm font-medium">counts</div>
              <el-upload
                  drag
                  action="#"
                  :file-list="fileListA2_2"
                  :on-change="onFileChangeA2_2"
                  :on-remove="onFileRemoveA2_2"
                  :auto-upload="false"
                  :limit="1"
                  :show-file-list="true"
                  accept=".csv,.tsv,.xlsx,.xls,.mtx,.txt,.json"
                  class="w-full"
              >
                <div class="el-upload__text">
                  {{$t('Pipelines_drag_upload')}} <em>{{$t('Pipelines_click_upload')}}</em>
                </div>
              </el-upload>
            </div>

            <div class="flex items-center justify-between pt-1">
              <el-button
                  type="primary"
                  @click="uploadFileA2_1(); uploadFileA2_2()"
                  :loading="uploadingA2_1 && uploadingA2_2"
              >
                {{$t('Pipelines_upload')}}
              </el-button>
              <el-button type="primary" :disabled="!(is_uploadedA2_1 && is_uploadedA2_2)" @click="putDatabase">{{$t('Pipelines_btn_put_database')}}</el-button>
            </div>
          </div>
        </el-card>
      </div>

      <!-- A3：Rawdata 上传路径 -->
      <div class="relative">
        <!-- 未解锁遮罩（仅视觉，实际逻辑后续接入） -->
<!--        <div class="absolute inset-0 rounded-xl bg-gradient-to-b from-white/60 to-white/30 dark:from-gray-900/60 dark:to-gray-900/30 backdrop-blur-[2px] border border-dashed border-gray-300 dark:border-gray-700 flex items-center justify-center z-10">-->
<!--          <div class="flex items-center gap-2">-->
<!--            <el-tag type="info" effect="dark" round>未解锁</el-tag>-->
<!--            <span class="text-sm text-gray-600 dark:text-gray-300">完成 A1 后可用</span>-->
<!--          </div>-->
<!--        </div>-->

        <el-card class="rounded-xl shadow-md border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900">
          <template #header>
            <div class="flex items-center justify-between">
              <span class="text-base font-semibold">A3｜{{$t('Pipelines_rawdata_upload')}}</span>

              <el-tag :type="is_uploadedA3 ? 'success' : 'info'"
                      effect="dark" round
              >
                {{ is_uploadedA3 ? $t('Pipelines_uploaded') : $t('Pipelines_pending_upload') }}
              </el-tag>
            </div>
          </template>

          <div class="space-y-5">
            <el-upload
                drag
                multiple
                action="#"
                :auto-upload="false"
                :file-list="fileListA3"
                :on-change="onFileChangeA3"
                :on-remove="onFileRemoveA3"
                :limit="100"
                :show-file-list="true"
                accept=".fastq,.fastq.gz,.fq,.fq.gz,.bam,.cram,.fast5,.zip,.tar,.gz"
                class="w-full"
            >
              <div class="el-upload__text">
                {{$t('Pipelines_drag_upload')}} <em>{{$t('Pipelines_click_upload')}}</em>
              </div>
              <template #tip>
                <div class="text-xs text-gray-500 dark:text-gray-400 mt-2">
                  {{$t('Pipelines_file_size')}}
                </div>
              </template>
            </el-upload>

            <div class="flex flex-wrap items-center gap-3">
              <el-button
                  type="primary"
                  @click="upload_rawdata_md5_check"
                  :loading="uploadingA3"
              >
                {{$t('Pipelines_upload')}}
              </el-button>
              <el-button type="primary" :disabled="!(is_uploadedA3 && check_md5)" @click="raw_processing">{{$t('Pipelines_btn_start_upstream')}}</el-button>
<!--              <el-button :disabled="!(upstream_loading)" @click="getRawdataStatus">{{$t('Pipelines_btn_upstream_status')}}</el-button>-->
<!--              <el-button type="success" :disabled="!(upstream_success)" @click="handle_upstream_result">{{$t('Pipelines_btn_upstream_result')}}</el-button>-->
<!--              <el-button type="primary" :disabled="!(upstream_success)" @click="putDatabase">{{$t('Pipelines_btn_put_database')}}</el-button>-->
              <el-button @click="getRawdataStatus">{{$t('Pipelines_btn_upstream_status')}}</el-button>
              <el-button type="success" @click="handle_upstream_result">{{$t('Pipelines_btn_upstream_result')}}</el-button>
              <el-button type="primary" @click="putDatabase">{{$t('Pipelines_btn_put_database')}}</el-button>
            </div>

            <el-descriptions :column="1" size="small" class="mt-2">
<!--              <el-descriptions-item label="会话 ID">-</el-descriptions-item>-->
              <el-descriptions-item :label="$t('Pipelines_analysis_status')">
                <el-tag
                    :type="upstream_status === 'unknown' ? 'info' : (upstream_status === 'running' || 'pending' ? 'warning' : 'success')"
                    round
                >
                  {{ upstream_status === 'unknown' ? $t('Pipelines_unknown') : upstream_status === 'running' ? $t('Pipelines_running') : upstream_status === 'pending' ? $t('Pipelines_pending') : upstream_status === 'failed' ? $t('Pipelines_failed') : $t('Pipelines_finished') }}
                </el-tag>


              </el-descriptions-item>
              <el-descriptions-item :label="$t('Pipelines_pre_result')">

                <el-tag
                    :type="upstream_success ? 'success' : 'info'"
                    round
                >
                  {{ upstream_success ? $t('Pipelines_ready') : $t('Pipelines_not_ready') }}
                </el-tag>

              </el-descriptions-item>
            </el-descriptions>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 说明 -->
    <div class="text-xs text-gray-500 dark:text-gray-400">

    </div>

  </div>

  <!-- 悬浮上传进度栏 -->
  <el-drawer
      v-model="showUploadPanel"
      direction="rtl"
      size="350px"
      :with-header="false"
      custom-class="upload-progress-drawer"
  >
    <div class="p-4">
      <div class="font-bold mb-2">任务上传进度</div>
<!--      <div v-if="fileListA1.length">-->
<!--        <div class="text-xs mb-1">A1 样本文件</div>-->
<!--        <el-progress-->
<!--            :percentage="fileListA1[0].percentage || 0"-->
<!--            :status="fileListA1[0].status === 'fail' ? 'exception' : undefined"-->
<!--            class="mb-2"-->
<!--        />-->
<!--      </div>-->
      <div v-if="fileListA3.length">
        <div class="text-xs mb-1">A3 Rawdata 文件</div>
        <div v-for="(file, idx) in fileListA3" :key="file.uid" class="mb-2">
          <div class="truncate text-xs">{{ file.name }}</div>
          <div class="flex items-center gap-2">
            <el-progress
                :percentage="file.percentage || 0"
                :status="file.status === 'fail' ? 'exception' : undefined"
                :text-inside="true"
                :stroke-width="16"
                class="flex-1"
            />
            <el-button
                v-if="file.status !== 'paused'"
                @click="pauseUploadA3(file)"
                circle

            >
              <el-icon :size="24">
                <VideoPause />
              </el-icon>
            </el-button>

            <el-button
                v-else
                @click="resumeUploadA3(file)"
                circle

            >
              <el-icon :size="24">
                <CaretRight />
              </el-icon>
            </el-button>

          </div>
        </div>
      </div>
      <div v-if="!fileListA1.length && !fileListA3.length" class="text-gray-400 text-xs">
        暂无上传任务
      </div>
    </div>
  </el-drawer>

  <!-- 悬浮按钮 -->
  <div
      class="fixed top-1/2 right-0 z-50 flex items-center"
      style="transform: translateY(-50%);"
  >
    <el-button
        type="primary"
        circle
        @click="showUploadPanel = !showUploadPanel"
        style="box-shadow: 0 2px 8px rgba(0,0,0,0.08);"
    >
      <el-icon>
        <i :class="showUploadPanel ? 'el-icon-close' : 'el-icon-upload'"></i>
      </el-icon>
    </el-button>
  </div>
  <PageFooter/>
</template>

<style scoped>


/* 调整 el-card 头部内边距以更紧凑 */
:deep(.el-card__header) {
  padding: 14px 16px;
}

.upload-progress-drawer {
  border-top-left-radius: 1rem;
  border-bottom-left-radius: 1rem;
  box-shadow: -2px 0 8px rgba(0,0,0,0.08);
}


</style>
<script setup lang="ts">
import { ref,watch,computed, onUnmounted } from 'vue';
import {useUpload} from '@/stores/modules/upload.ts'
import {uploadSampleSheet,uploadGeneExTpm,uploadGeneExCounts,uploadTranscriptFile,rawdataMd5Check,rawdataProcessing,getRawdataProcessingStatus} from '@/api/system.ts'
import {putDatabase, getRawdataResults} from '@/api/index.ts'
import {CaretRight, VideoPause} from "@element-plus/icons-vue";
import * as system from "@/api/system.ts";
import {ElNotification} from "element-plus";
import PageFooter from "@/components/page_footer.vue";

// 轮询定时器
const pollingTimer = ref<number | null>(null);

/* 控制悬浮进度栏显示 */
const showUploadPanel = ref(false);
const check_md5 = ref(false);

const upstream_loading = ref(false);

const upstream_success = ref(false);

type UpstreamStatus = 'unknown' | 'pending' | 'running' | 'finished';

const upstream_status = ref<UpstreamStatus>("unknown");

const upstream_result = ref<any[]>(null);

// 第一个上传
const {
  fileList: fileListA1,
  uploading: uploadingA1,
  is_uploaded: is_uploadedA1,
  onFileChange: onFileChangeA1,
  onFileRemove: onFileRemoveA1,
  uploadFile: uploadFileA1
} = useUpload({
  uploadApi: uploadSampleSheet
})

const {
  fileList: fileListA2_1,
  uploading: uploadingA2_1,
  is_uploaded: is_uploadedA2_1,
  onFileChange: onFileChangeA2_1,
  onFileRemove: onFileRemoveA2_1,
  uploadFile: uploadFileA2_1
} = useUpload({
  uploadApi: uploadGeneExTpm
})

const {
  fileList: fileListA2_2,
  uploading: uploadingA2_2,
  is_uploaded: is_uploadedA2_2,
  onFileChange: onFileChangeA2_2,
  onFileRemove: onFileRemoveA2_2,
  uploadFile: uploadFileA2_2
} = useUpload({
  uploadApi: uploadGeneExCounts
})

// 第三个上传
const {
  fileList: fileListA3,
  uploading: uploadingA3,
  is_uploaded: is_uploadedA3,
  progressList: progressListA3,
  onFileChange: onFileChangeA3,
  onFileRemove: onFileRemoveA3,
  uploadFile: uploadFileA3
} = useUpload({
  uploadApi: uploadTranscriptFile,
  formDataBuilder: (rawFile) => rawFile
})

async function upload_rawdata_md5_check() {
  await uploadFileA3();
  if (is_uploadedA3) {
    check_md5.value = await rawdataMd5Check(fileListA3.value.map(file => file.name)).then((res): any => {
        if (res.code === 0) {
          ElNotification({
            type: 'success',
            message: 'md5校验成功',
            duration: 2000,
          });
          return true;
        } else {
          ElNotification({
            type: 'error',
            message: 'md5校验失败',
          });
          return false;
        }
      }).catch((error) => {
        ElNotification({
          type: 'error',
          message: 'md5校验失败',
          duration: 2000,
        });
        return false;
      });
  }else {
    check_md5.value = false;
  }
}


async function raw_processing() {
  rawdataProcessing().then((res): any => {
    if (res.code === 0) {
      ElNotification({
        type: 'success',
        message: '上游分析启动成功',
        duration: 2000,
      });
      upstream_loading.value = true;
    } else {
      ElNotification({
        type: 'error',
        message: '上游分析启动失败',
      });
      upstream_loading.value = false;
    }
  }).catch((error) => {
    ElNotification({
      type: 'error',
      message: '上游分析启动失败',
      duration: 2000,
    });
    upstream_loading.value = false;
  });
}

async function getRawdataStatus() {
  getRawdataProcessingStatus().then((res): any => {
    upstream_status.value = res.data?.status || "unknown";
    if (res.data && res.data.status === 'finished') {
      upstream_success.value = true;
      upstream_loading.value = false
    } else if(res.data && res.data.status === 'running'){
      upstream_success.value = false;
      upstream_loading.value = true;
    } else {
      upstream_success.value = false;
      upstream_loading.value = false
    }
  }).catch((error) => {
    //上游分析失败
    upstream_success.value = false;
    //分析过程中断
    upstream_loading.value = false
  });
}

async function handle_upstream_result() {
  upstream_result.value = await getRawdataResults();
  await exportAllCSVs();
}


watch(upstream_loading, (val) => {
  if (val) {
    // 启动轮询
    getRawdataStatus(); // 立即执行一次
    pollingTimer.value = window.setInterval(() => {
      getRawdataStatus();
    }, 5000);
  } else {
    // 停止轮询
    if (pollingTimer.value) {
      clearInterval(pollingTimer.value);
      pollingTimer.value = null;
    }
  }
});

// 动态生成列
function getColumns(data: any[]) {
  if (!data || !data.length) return [];
  return Object.keys(data[0]).map(key => ({
    prop: key,
    label: key
  }));
}


// 工具：把数据转为 CSV 文本（含 BOM，Excel 友好）
function toCsv(data: any[]): string {
  const columns = getColumns(data);
  const headers = columns.map(c => c.label);
  const keys = columns.map(c => String(c.prop ?? c.label));

  const rows = data.map(row => keys.map(k => row?.[k]));
  const csvBody = [headers, ...rows]
      .map(r => r.map(v => {
        const s = String(v ?? '');
        // 转义双引号，并包裹引号，兼容逗号/换行/制表符
        const escaped = s.replace(/"/g, '""');
        return `"${escaped}"`;
      }).join(','))
      .join('\r\n');

  // 前置 BOM，避免 Excel 乱码
  return '\ufeff' + csvBody;
}

// 工具：触发下载
function downloadCsv(filename: string, csvContent: string) {
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  // 异步释放，确保下载已触发
  setTimeout(() => URL.revokeObjectURL(url), 0);
}

// 单表导出：按 key 导出
function exportCSV(tableKey: string) {
  const source = upstream_result?.value as Record<string, any[]> | null | undefined;
  if (!source || typeof source !== 'object') return;

  const data = source[tableKey];
  if (!Array.isArray(data) || data.length === 0) return;

  downloadCsv(`${tableKey}.csv`, toCsv(data));
}

// 全部导出：遍历所有非空表
async function exportAllCSVs() {
  const source = upstream_result?.value as Record<string, any[]> | null | undefined;
  if (!source || typeof source !== 'object') return;

  const entries = Object.entries(source) as [string, any[]][];
  for (const [tableKey, data] of entries) {
    if (!Array.isArray(data) || data.length === 0) continue;
    downloadCsv(`${tableKey}.csv`, toCsv(data));
    // 间隔一下，降低被拦截概率
    await new Promise(r => setTimeout(r, 150));
  }
}


// 组件卸载时清理定时器
onUnmounted(() => {
  if (pollingTimer.value) {
    clearInterval(pollingTimer.value);
  }
});

</script>