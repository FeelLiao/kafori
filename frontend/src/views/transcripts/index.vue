<template>
  <div class="min-h-screen font-sans antialiased bg-gray-50 text-gray-800 dark:bg-gray-900 dark:text-gray-100 flex relative transition-colors">
    <!-- 左侧导航 -->
    <Aside :active-section="activeSection" @navigate="scrollToSection" />

    <!-- 主内容区 -->
    <main class="main-content">
      <!-- 实验列表部分 -->
      <div ref="experimentSectionEl" class="section">
        <ExperimentSection
            @update:selectedExperimentIds="(ids) => (selectedExperimentIds.value = ids as any)"
            @fetch-samples="handleFetchSamples"
        />
      </div>

      <!-- 样本列表部分 -->
      <div ref="sampleSectionEl" class="section">
        <SampleSection
            :samples="sampleData"
            @update:selectedSampleIds="handleSelectedSampleIds"
            @analyzed="handleAnalyzed"
        />
      </div>

      <!-- 实验结果部分 -->
      <div ref="resultSectionEl" class="section result-section">
        <ResultSection
            :res="transcriptRes"
            @analyzed="handleAnalyzed"
            :selectedSampleIds="selectedSampleIds"
            :width="plotWidth"
            :height="plotHeight"
        />
      </div>
    </main>
  </div>
</template>

<style scoped>

.main-content {
  flex: 1 1 0%;
  display: flex;
  flex-direction: column;
  min-width: 0;
  padding-left: 16rem; /* 侧边栏宽度 */
  padding-right: 2rem;
  padding-top: 2.5rem;
  padding-bottom: 2.5rem;
  overflow-x: auto;
  box-sizing: border-box;
}
.section {
  margin-bottom: 2rem;
  min-width: 0;
  overflow-x: auto;
}
.result-section {
  flex: 1 1 0%;
  min-height: 0;
  overflow: auto;
}
</style>


<script setup lang="ts">
import { ref, watch } from 'vue';
import Aside from './aside.vue';
import ExperimentSection from './ExperimentSection.vue';
import SampleSection from './SampleSection.vue';
import ResultSection from './ResultSection.vue';
import { transcriptsQuery } from '@/api/index.ts';
import type { Sample } from '@/api/interface.ts';

const activeSection = ref<'experiment' | 'sample' | 'result'>('experiment');

const experimentSectionEl = ref<HTMLElement | null>(null);
const sampleSectionEl = ref<HTMLElement | null>(null);
const resultSectionEl = ref<HTMLElement | null>(null);

function scrollToSection(section: 'experiment' | 'sample' | 'result') {
  activeSection.value = section;
  let el: HTMLElement | null = null;
  if (section === 'experiment') el = experimentSectionEl.value;
  if (section === 'sample') el = sampleSectionEl.value;
  if (section === 'result') el = resultSectionEl.value;
  el?.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// 与样本检索相关的状态
const selectedExperimentIds = ref<Array<string | number>>([]);
const selectedSampleIds = ref<Array<string | number>>([]);

const sampleData = ref<Sample[]>([]);

async function handleFetchSamples(ids: Array<string | number>) {
  // ids 可以是勾选的，也可以是单个 UniqueEXID
  sampleData.value = await transcriptsQuery('sample_id', ids);
}

// 监听变化并输出
// watch(selectedExperimentIds, (newVal, oldVal) => {
//   console.log('selectedExperimentIds8 变化:', newVal);
// });
//
//
// // 监听变化并输出
// watch(selectedSampleIds, (newVal, oldVal) => {
//   console.log('selectedSampleIds 变化:', newVal);
// });

// 分析结果
const transcriptRes = ref<any>(null);
const plotWidth = ref(900);
const plotHeight = ref(600);

function handleAnalyzed(payload: { res: any; width: number; height: number }) {
  transcriptRes.value = payload.res;
  plotWidth.value = payload.width;
  plotHeight.value = payload.height;
  // 切换到结果区域
  scrollToSection('result');
}

// ... 其余不变 ...
function handleSelectedSampleIds(ids: Array<string | number>) {
  // console.log('[Parent] 收到 selectedSampleIds ->', ids); // <- 增加日志确认
  selectedSampleIds.value = ids;
}
</script>