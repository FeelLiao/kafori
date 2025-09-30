<template>
  <div class="min-h-screen font-sans antialiased bg-gray-50 text-gray-800 dark:bg-gray-900 dark:text-gray-100 flex relative transition-colors">
    <!-- 左侧导航 -->
    <Aside :active-section="activeSection" @navigate="scrollToSection" />

    <!-- 主内容区 -->
    <main class="main-content">
      <!-- 实验列表部分 -->
      <div ref="experimentSectionEl" class="section">
        <ExperimentSection
            @update:selectedExperimentIds="(ids) => (selectedExperimentIds = ids as any)"
            @fetch-samples="handleFetchSamples"
        />
      </div>

      <!-- 样本列表部分 -->
      <div ref="sampleSectionEl" class="section">
        <SampleSection
            :samples="sampleData"
            @analyzed="handleAnalyzed"
        />
      </div>

      <!-- 实验结果部分 -->
      <div ref="resultSectionEl" class="section result-section">
        <ResultSection :res="transcriptRes" :width="plotWidth" :height="plotHeight" />
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
import { ref } from 'vue';
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
let selectedExperimentIds = [] as Array<string | number>;
const sampleData = ref<Sample[]>([]);

async function handleFetchSamples() {
  // 基于实验选择检索样本
  sampleData.value = await transcriptsQuery('sample_id', selectedExperimentIds);
}

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
</script>