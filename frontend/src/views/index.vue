<!-- vue -->
<template>
  <div class="font-sans antialiased bg-gray-50 text-gray-800 dark:bg-gray-900 dark:text-gray-100 relative transition-colors">
    <!-- 粒子背景 -->
    <div id="particles-js"></div>

    <main>
      <!-- 英雄区域（满屏） -->
      <section class="section-full">
        <div class="container mx-auto px-4 h-full flex items-center">
          <div class="grid grid-cols-1 md:grid-cols-12 gap-8 items-center w-full">
            <div class="md:col-span-7">
              <h1 class="text-4xl md:text-5xl font-bold leading-tight mb-6">
                {{ $t('title', { type: '' }) }}<span class="text-cyan-500">{{$t('mRNA')}}</span>
                <span v-if="$i18n.locale === 'zh'">{{$t('the')}}{{$t('mystery')}}</span>
                <span v-else></span>
                <br />{{ $t('transcriptome_data_analysis_and', { Visualization: '' }) }}<span class="text-lime-400">{{$t('Visualization')}}</span>
                <span v-if="$i18n.locale === 'zh'">{{$t('Platform')}}</span>
                <span v-else>{{$t('blank')}}{{$t('Platform')}}</span>
              </h1>
              <p class="prose text-lg text-gray-600 dark:text-gray-300 mb-8">
                {{ $t('home_desc') }}
              </p>
              <div class="flex flex-wrap gap-4">
                <button
                    class="px-6 py-3 bg-gradient-to-r from-lime-400 to-cyan-400 text-white rounded-lg shadow-md hover:shadow-lg transition"
                    @click="scrollToDashboard"
                >
                  {{$t('home_start')}} <i class="fas fa-dna ml-2"></i>
                </button>
                <button
                    class="px-6 py-3 border border-cyan-400 text-cyan-500 rounded-lg hover:bg-cyan-50 dark:hover:bg-cyan-900 transition"
                    @click="openLearnMore"
                >
                  {{$t('home_more')}} <i class="fas fa-book-open ml-2"></i>
                </button>
              </div>
            </div>
            <div class="md:col-span-5 flex justify-center">
              <svg class="dna-helix w-full max-w-[480px] h-auto" viewBox="0 0 400 400" preserveAspectRatio="xMidYMid meet">
                <!-- DNA双螺旋结构 -->
                <path
                    d="M200,50 Q225,75 200,100 Q175,125 200,150 Q225,175 200,200 Q175,225 200,250 Q225,275 200,300 Q175,325 200,350"
                    stroke="url(#dna-gradient1)"
                    stroke-width="4"
                    fill="none"
                />
                <path
                    d="M200,50 Q175,75 200,100 Q225,125 200,150 Q175,175 200,200 Q225,225 200,250 Q175,275 200,300 Q225,325 200,350"
                    stroke="url(#dna-gradient2)"
                    stroke-width="4"
                    fill="none"
                />
                <!-- 碱基对连接线 -->
                <line x1="200" y1="50" x2="200" y2="50" stroke="rgba(127,255,0,0.5)" stroke-width="2">
                  <animate attributeName="y2" values="50;50;100;100" keyTimes="0;0.25;0.5;1" dur="3s" repeatCount="indefinite"/>
                </line>
                <line x1="200" y1="100" x2="200" y2="100" stroke="rgba(0,255,255,0.5)" stroke-width="2">
                  <animate attributeName="y2" values="100;100;150;150" keyTimes="0;0.25;0.5;1" dur="3s" begin="0.75s" repeatCount="indefinite"/>
                </line>
                <line x1="200" y1="150" x2="200" y2="150" stroke="rgba(127,255,0,0.5)" stroke-width="2">
                  <animate attributeName="y2" values="150;150;200;200" keyTimes="0;0.25;0.5;1" dur="3s" begin="1.5s" repeatCount="indefinite"/>
                </line>
                <line x1="200" y1="200" x2="200" y2="200" stroke="rgba(0,255,255,0.5)" stroke-width="2">
                  <animate attributeName="y2" values="200;200;250;250" keyTimes="0;0.25;0.5;1" dur="3s" begin="2.25s" repeatCount="indefinite"/>
                </line>
                <line x1="200" y1="250" x2="200" y2="250" stroke="rgba(127,255,0,0.5)" stroke-width="2">
                  <animate attributeName="y2" values="250;250;300;300" keyTimes="0;0.25;0.5;1" dur="3s" begin="3s" repeatCount="indefinite"/>
                </line>
                <line x1="200" y1="300" x2="200" y2="300" stroke="rgba(0,255,255,0.5)" stroke-width="2">
                  <animate attributeName="y2" values="300;300;350;350" keyTimes="0;0.25;0.5;1" dur="3s" begin="3.75s" repeatCount="indefinite"/>
                </line>
                <defs>
                  <linearGradient id="dna-gradient1" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#7FFF00" />
                    <stop offset="100%" stop-color="#00FFFF" />
                  </linearGradient>
                  <linearGradient id="dna-gradient2" x1="100%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stop-color="#00FFFF" />
                    <stop offset="100%" stop-color="#7FFF00" />
                  </linearGradient>
                </defs>
              </svg>
            </div>
          </div>
        </div>
      </section>

      <!-- 数据仪表盘（满屏） -->
      <section id="dashboard" class="section-full bg-gray-100 dark:bg-gray-900">
        <div class="container mx-auto px-4 h-full flex items-center">
          <div class="w-full">
            <h2 class="text-3xl font-bold text-center mb-8 md:mb-12">
              <span class="text-cyan-500">{{$t('home_data_dashboard')}}</span>
            </h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8 h-[calc(100%-4rem)]">
              <div class="md:col-span-1 bg-white dark:bg-gray-800 dark:text-gray-100 rounded-xl shadow-md p-6 flex flex-col">
                <h3 class="text-xl font-semibold mb-4">{{$t('home_year_map')}}</h3>
                <div ref="basePairChartRef" style="width:100%;flex:1;min-height:300px;"></div>
                <p class="prose text-sm text-gray-600 dark:text-gray-400 mt-4">
                  {{$t('home_year_mapDesc')}}
                </p>
              </div>
              <div class="md:col-span-1 bg-white dark:bg-gray-800 dark:text-gray-100 rounded-xl shadow-md p-6 flex flex-col">
                <h3 class="text-xl font-semibold mb-4">{{$t('home_sample_map')}}</h3>
                <div ref="chartRef" style="width:100%;flex:1;min-height:320px;"></div>
                <p class="prose text-sm text-gray-600 dark:text-gray-400 mt-4">
                  {{$t('home_sample_mapDesc')}}
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 基因序列展示（满屏） -->
      <section class="section-full bg-white dark:bg-gray-900">
        <div class="container mx-auto px-4 h-full flex items-center">
          <div class="w-full">
            <h2 class="text-3xl font-bold text-center mb-12">基因序列<span class="text-lime-500">浏览器</span></h2>
            <div class="bg-gray-800 rounded-lg p-4 overflow-hidden">
              <div class="flex justify-between items-center mb-4">
                <div class="text-gray-300 font-mono">Chr1: 15,000-15,500</div>
                <div class="flex space-x-2">
                  <button class="px-3 py-1 bg-gray-700 text-gray-300 rounded hover:bg-gray-600">
                    <i class="fas fa-search"></i>
                  </button>
                  <button class="px-3 py-1 bg-gray-700 text-gray-300 rounded hover:bg-gray-600">
                    <i class="fas fa-download"></i>
                  </button>
                </div>
              </div>
              <div class="overflow-x-auto">
                <div class="sequence-scroll inline-block whitespace-nowrap">
                  <div class="inline-block courier-new text-sm text-gray-100">
                    <span class="text-lime-300">ATG</span>
                    <span class="text-cyan-300">CGA</span>
                    <span class="text-amber-300">TTA</span>
                    <span class="text-purple-300">GCT</span>
                    <span class="text-lime-300">AAC</span>
                    <span class="text-cyan-300">GGA</span>
                    <span class="text-amber-300">TCC</span>
                    <span class="text-purple-300">GTA</span>
                    <span class="text-lime-300">ATG</span>
                    <span class="text-cyan-300">CGA</span>
                    <span class="text-amber-300">TTA</span>
                    <span class="text-purple-300">GCT</span>
                    <span class="text-lime-300">AAC</span>
                    <span class="text-cyan-300">GGA</span>
                    <span class="text-amber-300">TCC</span>
                    <span class="text-purple-300">GTA</span>
                    <span class="text-lime-300">ATG</span>
                    <span class="text-cyan-300">CGA</span>
                    <span class="text-amber-300">TTA</span>
                    <span class="text-purple-300">GCT</span>
                    <span class="text-lime-300">AAC</span>
                    <span class="text-cyan-300">GGA</span>
                    <span class="text-amber-300">TCC</span>
                    <span class="text-purple-300">GTA</span>
                    <span class="text-lime-300">ATG</span>
                    <span class="text-cyan-300">CGA</span>
                    <span class="text-amber-300">TTA</span>
                    <span class="text-purple-300">GCT</span>
                    <span class="text-lime-300">AAC</span>
                    <span class="text-cyan-300">GGA</span>
                    <span class="text-amber-300">TCC</span>
                    <span class="text-purple-300">GTA</span>
                  </div>
                </div>
              </div>
              <div class="mt-4 flex justify-between text-xs text-gray-400">
                <div>正向链</div>
                <div>500 bp</div>
              </div>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8 mt-12">
              <div class="bg-gray-50 dark:bg-gray-800 dark:text-gray-100 rounded-lg p-6">
                <h3 class="text-xl font-semibold mb-4">序列特征分析</h3>
                <div class="prose">
                  <p class="dark:text-gray-300">DNA序列特征分析可以揭示基因组的编码潜力、重复序列分布以及进化关系等信息。</p>
                  <p>不同颜色的三联密码子代表不同类型的氨基酸编码特性：</p>
                  <ul class="list-disc pl-5 space-y-2">
                    <li><span class="text-lime-500">绿色</span>：疏水性氨基酸</li>
                    <li><span class="text-cyan-500">青色</span>：极性不带电氨基酸</li>
                    <li><span class="text-amber-500">橙色</span>：酸性氨基酸</li>
                    <li><span class="text-purple-500">紫色</span>：碱性氨基酸</li>
                  </ul>
                </div>
              </div>
              <div class="bg-gray-50 dark:bg-gray-800 dark:text-gray-100 rounded-lg p-6">
                <h3 class="text-xl font-semibold mb-4">功能注释</h3>
                <div class="prose">
                  <p class="dark:text-gray-300">通过生物信息学方法预测的序列功能注释可以帮助研究者快速识别潜在的功能区域。</p>
                  <div class="mt-4">
                    <div class="flex justify-between text-sm mb-1">
                      <span>编码区(CDS)</span>
                      <span>42%</span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-2">
                      <div class="bg-lime-400 h-2 rounded-full" style="width: 42%"></div>
                    </div>
                  </div>
                  <div class="mt-4">
                    <div class="flex justify-between text-sm mb-1">
                      <span>调控区</span>
                      <span>18%</span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-2">
                      <div class="bg-cyan-400 h-2 rounded-full" style="width: 18%"></div>
                    </div>
                  </div>
                  <div class="mt-4">
                    <div class="flex justify-between text-sm mb-1">
                      <span>重复序列</span>
                      <span>25%</span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-2">
                      <div class="bg-amber-400 h-2 rounded-full" style="width: 25%"></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 3D DNA结构（满屏） -->
      <section class="section-full bg-gray-100 dark:bg-gray-900">
        <div class="container mx-auto px-4 h-full flex items-center">
          <div class="grid grid-cols-1 md:grid-cols-12 gap-8 w-full">
            <div class="md:col-span-7">
              <div ref="dna3dChartRef" style="width:100%;min-height:320px;background:#f8fafc;"></div>
            </div>
            <div class="md:col-span-5">
              <h3 class="text-2xl font-semibold mb-4">交互式DNA双螺旋</h3>
              <div class="prose">
                <p class="dark:text-gray-300">通过鼠标拖拽可以旋转查看DNA双螺旋结构的三维模型，滚轮可缩放观察细节。</p>
                <p>模型展示了DNA分子的主要结构特征：</p>
                <ul class="list-disc pl-5 space-y-2">
                  <li>大沟和小沟的周期性变化</li>
                  <li>碱基对的平面堆叠</li>
                  <li>磷酸骨架的走向</li>
                  <li>螺旋的右手性</li>
                </ul>
              </div>
              <div class="mt-6 grid grid-cols-2 gap-4">
                <div class="bg-white dark:bg-gray-800 dark:text-cyan-300 p-4 rounded-lg shadow-sm">
                  <div class="text-cyan-500 dark:text-cyan-300 text-xl font-bold">10.5</div>
                  <div class="text-sm text-gray-600 dark:text-gray-400">每圈碱基数</div>
                </div>
                <div class="bg-white dark:bg-gray-800 dark:text-lime-300 p-4 rounded-lg shadow-sm">
                  <div class="text-lime-500 dark:text-lime-300 text-xl font-bold">3.4nm</div>
                  <div class="text-sm text-gray-600 dark:text-gray-400">每圈高度</div>
                </div>
                <div class="bg-white dark:bg-gray-800 dark:text-purple-300 p-4 rounded-lg shadow-sm">
                  <div class="text-purple-500 dark:text-purple-300 text-xl font-bold">2nm</div>
                  <div class="text-sm text-gray-600 dark:text-gray-400">双螺旋直径</div>
                </div>
                <div class="bg-white dark:bg-gray-800 dark:text-amber-300 p-4 rounded-lg shadow-sm">
                  <div class="text-amber-500 dark:text-amber-300 text-xl font-bold">0.34nm</div>
                  <div class="text-sm text-gray-600 dark:text-gray-400">碱基间距</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 关于平台（满屏） -->
      <section class="section-full bg-white dark:bg-gray-900">
        <div class="container mx-auto px-4 h-full flex items-center">
          <div class="w-full">
            <h2 class="text-3xl font-bold text-center mb-12">关于<span class="text-lime-500">平台</span></h2>
            <div class="grid grid-cols-1 md:grid-cols-12 gap-8">
              <div class="md:col-span-7">
                <div class="prose">
                  <h3 class="text-2xl font-semibold mb-4">技术架构</h3>
                  <p class="dark:text-gray-300">本平台采用现代Web技术构建，主要技术栈包括：</p>
                  <ul class="list-disc pl-5 space-y-2">
                    <li>前端框架：React + Tailwind CSS</li>
                    <li>可视化库：D3.js + ECharts</li>
                    <li>3D渲染：Three.js</li>
                    <li>数据分析：Python + Biopython</li>
                    <li>数据存储：MongoDB + PostgreSQL</li>
                  </ul>
                  <h3 class="text-2xl font-semibold mt-8 mb-4">数据来源</h3>
                  <p class="dark:text-gray-300">平台整合了多个公共数据库的基因组数据，包括：</p>
                  <ul class="list-disc pl-5 space-y-2">
                    <li>NCBI GenBank</li>
                    <li>Ensembl Genome Browser</li>
                    <li>UCSC Genome Browser</li>
                    <li>DNA Data Bank of Japan (DDBJ)</li>
                  </ul>
                </div>
              </div>
              <div class="md:col-span-5">
                <div class="bg-gray-50 dark:bg-gray-800 dark:text-gray-100 p-6 rounded-lg">
                  <h3 class="text-xl font-semibold mb-4">获取数据</h3>
                  <form class="space-y-4">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">基因组版本</label>
                      <select class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-cyan-500">
                        <option>GRCh38 (hg38)</option>
                        <option>GRCh37 (hg19)</option>
                        <option>NCBI36 (hg18)</option>
                      </select>
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">染色体</label>
                      <select class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-cyan-500">
                        <option>1号染色体</option>
                        <option>2号染色体</option>
                        <option>X染色体</option>
                        <option>Y染色体</option>
                        <option>线粒体DNA</option>
                      </select>
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">起始位置</label>
                      <input type="number" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-cyan-500" />
                    </div>
                    <div>
                      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">结束位置</label>
                      <input type="number" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-cyan-500" />
                    </div>
                    <button type="submit" class="w-full py-2 px-4 bg-gradient-to-r from-lime-400 to-cyan-400 text-white rounded-md shadow hover:shadow-md transition">
                      获取序列数据
                    </button>
                  </form>
                </div>
              </div>
            </div>
            <div class="border-t border-gray-200 dark:border-gray-700 mt-8 pt-8 text-center text-sm">
              <p>© 2025 转录组分析平台. 保留所有权利.</p>
              <p class="mt-2 text-gray-500" style="font-size:16pt">Copyright 2025，Feeliao/Feelzhou</p>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed, watch } from 'vue'
import * as echarts from 'echarts'
import type { ExpClassDTO } from '@/api/interface.ts'
import { getAllExpCounts, getYearCounts, transcriptsQuery } from '@/api/index.ts'

/* DOM refs */
const basePairChartRef = ref<HTMLElement | null>(null)
const chartRef = ref<HTMLDivElement | null>(null)
const dna3dChartRef = ref<HTMLElement | null>(null)

/* ECharts instances */
let basePairChartInst: echarts.ECharts | null = null
let sampleChartInst: echarts.ECharts | null = null

/* 数据 */
const exp_data = ref<ExpClassDTO | null>(null)
const exp_counts = ref<any[]>([])
const year_counts = ref<any[]>([])

/* 派生数据 */
const xData = computed(() => (exp_counts.value || []).map(d => ellipsis(String(d.Experiment ?? ''), 12)))
const barData = computed(() => (exp_counts.value || []).map(d => Number(d.count ?? 0)))
const lineData = computed(() => (exp_counts.value || []).map(d => Number(d.count ?? 0)))

const pieData = computed(() =>
    (year_counts.value || []).map((d: any) => ({
      name: String(d?.Year ?? ''),
      value: Number(d?.count ?? 0),
    }))
)

/* 辅助与样式 */
const categoryColor: Record<string, string> = {
  s1: '#3b82f6',
  s2: '#10b981',
  s3: '#f59e42',
}

function ellipsis(str: string, max = 12) {
  return str.length > max ? str.slice(0, max) + '...' : str
}

function scrollToDashboard() {
  document.getElementById('dashboard')?.scrollIntoView({ behavior: 'smooth' })
}

function openLearnMore() {
  window.open('https://github.com/feelliao/kafori/', '_blank')
}

/* 渲染函数 */
function renderBasePairChart(data: { name: string; value: number }[]) {
  if (!basePairChartInst) return
  basePairChartInst.setOption({
    tooltip: { trigger: 'item' },
    legend: { bottom: 0 },
    series: [
      {
        name: '年份样本占比',
        type: 'pie',
        radius: ['40%', '70%'],
        data,
        label: { formatter: '{b}: {d}%' },
        avoidLabelOverlap: true,
      },
    ],
  })
}

function initSampleChart() {
  if (!sampleChartInst) return
  sampleChartInst.setOption({
    tooltip: {
      trigger: 'axis',
      formatter: params => {
        const idx = params?.[0]?.dataIndex ?? 0
        const item = exp_counts.value[idx] || {}
        const cat = item.ExperimentCategory || 's1'
        const color = categoryColor[cat] || '#1197cc'
        return `
          <div style="display:flex;align-items:center;margin-bottom:6px;">
            <span style="display:inline-block;width:12px;height:12px;background:${color};border-radius:3px;margin-right:6px;"></span>
            <span style="font-weight:bold;">${cat}</span>
          </div>
          <div>
            <strong>Experiment:</strong> ${item.Experiment ?? ''}<br/>
            <strong>SampleCounts:</strong> ${item.count ?? 0}
          </div>
        `
      },
    },
    grid: { left: 36, right: 36, top: 36, bottom: 36 },
    xAxis: {
      type: 'category',
      name: 'Experiment',
      nameLocation: 'middle',
      nameGap: 30,
      data: xData.value,
      axisLabel: { formatter: (value: string) => value, interval: 0, showMaxLabel: true },
    },
    yAxis: {
      type: 'value',
      name: 'SampleCounts',
      nameLocation: 'middle',
      nameGap: 40,
    },
    series: [
      {
        name: 'SampleCounts',
        type: 'bar',
        data: barData.value,
        barWidth: 40,
        itemStyle: {
          borderRadius: [6, 6, 0, 0],
          color: ({ dataIndex }) =>
              categoryColor[exp_counts.value?.[dataIndex]?.ExperimentCategory] || '#1197cc',
        },
        label: { show: true, position: 'top', fontWeight: 'bold' },
      },
      {
        name: '趋势',
        type: 'line',
        data: lineData.value,
        symbol: 'circle',
        symbolSize: 10,
        lineStyle: { width: 3, color: '#76fa2a' },
        itemStyle: { color: '#76fa2a' },
        smooth: true,
      },
    ],
  })
}

/* 自适应 */
function handleResize() {
  basePairChartInst?.resize()
  sampleChartInst?.resize()
}

/* 数据获取（并发） */
async function fetchAll() {
  const [expClass, counts, years] = await Promise.all([
    transcriptsQuery('exp_class'),
    getAllExpCounts(),
    getYearCounts(),
  ])
  exp_data.value = expClass
  exp_counts.value = counts ?? []
  year_counts.value = years ?? []
}

onMounted(async () => {
  // 初始化图表实例
  if (basePairChartRef.value) {
    basePairChartInst = echarts.init(basePairChartRef.value)
  }
  if (chartRef.value) {
    sampleChartInst = echarts.init(chartRef.value)
    initSampleChart()
  }

  // 监听窗口尺寸变化
  window.addEventListener('resize', handleResize, { passive: true })

  // 获取数据
  await fetchAll()
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  basePairChartInst?.dispose()
  sampleChartInst?.dispose()
  basePairChartInst = null
  sampleChartInst = null
})

/* 数据变动时更新图表（增量） */
watch(pieData, (data) => {
  renderBasePairChart(data)
}, { immediate: true })

watch([xData, barData, lineData, () => exp_counts.value], ([newX, newBar, newLine]) => {
  if (!sampleChartInst) return
  sampleChartInst.setOption({
    xAxis: { data: newX },
    series: [{ data: newBar }, { data: newLine }],
  })
})
</script>

<style scoped>
/* 满屏 section：支持移动端动态视口（100svh） */
.section-full {
  min-height: 100svh;
  display: flex;
  align-items: center;
}

/* 背景铺满整个页面而非仅首屏 */
#particles-js {
  position: fixed;
  inset: 0;
  z-index: -1;
}

@keyframes dna-spin {
  0% { transform: rotateY(0); }
  100% { transform: rotateY(360deg); }
}
@keyframes sequence-scroll {
  0% { transform: translateX(0); }
  100% { transform: translateX(-50%); }
}
.dna-helix {
  animation: dna-spin 30s linear infinite;
}
.sequence-scroll {
  animation: sequence-scroll 30s linear infinite;
}
.courier-new {
  font-family: 'Courier New', Courier, monospace;
}
.prose p {
  text-align: justify;
  hyphens: auto;
  margin-bottom: 1rem;
}
</style>
