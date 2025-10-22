<template>
  <div class="min-h-screen font-sans antialiased bg-gray-50 text-gray-800 dark:bg-gray-900 dark:text-gray-100 flex relative transition-colors">

    <!-- 主内容区 -->
    <main class="flex-1 py-10 bg-transparent">

      <!-- 样本列表部分 -->
      <div ref="DownloadSectionEl">
        <DownloadSection
            :samples="sampleData"
            @analyzed="handleAnalyzed"
        />
      </div>

    </main>

  </div>
  <PageFooter/>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import DownloadSection from './DownloadSection.vue';
import { transcriptsQuery,getDownloadCatalog } from '@/api/index.ts';
import type { Sample } from '@/api/interface.ts';
import PageFooter from "@/components/page_footer.vue";

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
  const data = await getDownloadCatalog();

  sampleData.value = data.flatMap(entry =>
      Object.entries(entry.items).map(([item_type, item]) => ({
        classes: entry.classes,
        item_type,
        filename: item.filename,
        media_type: item.media_type,
      }))
  );
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

handleFetchSamples();

</script>