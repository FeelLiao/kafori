<template>
  <div class="min-h-screen bg-white dark:bg-black dark:bg-gray-900 transition-colors duration-300">
    <div class="grid grid-cols-1 md:grid-cols-3 gap-8 p-8">
      <el-card
          v-for="person in people"
          :key="person.name"
          class="flex flex-col items-center bg-white text-black dark:bg-gray-900 dark:text-white shadow-lg rounded-xl relative"
          style="padding-bottom:80px;"
      >
      <div class="flex flex-col items-center mb-4">
        <el-avatar :src="person.avatar" :size="100" class="mb-2" />
        <div class="font-bold text-xl">{{ person.name }}</div>
      </div>
      <div class="text-sm mb-4 text-gray-500 dark:text-gray-300 text-center px-2">{{ person.bio }}</div>
      <div
          class="flex gap-6 justify-center items-center absolute left-0 right-0 bottom-6"
      >
        <el-tooltip content="Email" placement="top">
          <el-icon
              class="cursor-pointer"
              style="font-size:45px;display:flex;align-items:center;justify-content:center;"
              @click="goTo(`mailto:${person.email}`)"
          >
            <Message />
          </el-icon>
        </el-tooltip>
        <el-tooltip content="Orcid" placement="top">
          <img
              src="/icon/orcid.svg"
              alt="ORCID"
              class="cursor-pointer"
              style="width:48px;height:48px;object-fit:contain;display:flex;align-items:center;justify-content:center;"
              @click="goTo(person.orcid)"
          />
        </el-tooltip>
        <el-tooltip content="Github" placement="top">
            <span class="flex items-center cursor-pointer">
              <img
                  src="/icon/github-mark.svg"
                  alt="Github"
                  class="block dark:hidden"
                  style="width:40px;height:40px;object-fit:contain;"
                  @click="goTo(person.github)"
              />
              <img
                  src="/icon/github-mark-white.svg"
                  alt="Github"
                  class="hidden dark:block"
                  style="width:40px;height:40px;object-fit:contain;"
                  @click="goTo(person.github)"
              />
            </span>
        </el-tooltip>
      </div>
      </el-card>
    </div>
    <!-- 补充内容区块 -->
    <div class="max-w-3xl mx-auto mt-12 p-8 bg-gray-100 dark:bg-gray-800 rounded-xl shadow text-center">
      <h2 class="text-2xl font-bold mb-4 text-gray-800 dark:text-gray-100">我们的团队</h2>
      <p class="mb-4 text-gray-600 dark:text-gray-300">
        我们致力于推动林业科学与信息技术的融合，欢迎更多志同道合的伙伴加入我们，共同探索数据驱动的生物研究新方向。
      </p>
      
    </div>
    <footer class="bg-gray-800 dark:bg-gray-900 text-gray-300 py-12">
      <div class="container mx-auto px-4">
        <div class="grid grid-cols-1 md:grid-cols-12 gap-8">
          <div class="md:col-span-4">
            <div class="flex items-center space-x-2 mb-4">
              <div class="w-8 h-8 rounded-full bg-gradient-to-br from-lime-400 to-cyan-400 dark:from-lime-700 dark:to-cyan-700"></div>
              <span class="text-xl font-bold text-white">基因解码</span>
            </div>
            <p class="text-sm">探索基因组奥秘的专业可视化平台，为生物医学研究提供数据支持。</p>
            <div class="flex space-x-4 mt-4">
              <a href="#" class="text-gray-400 hover:text-white transition"><i class="fab fa-github text-xl"></i></a>
              <a href="#" class="text-gray-400 hover:text-white transition"><i class="fab fa-twitter text-xl"></i></a>
              <a href="#" class="text-gray-400 hover:text-white transition"><i class="fab fa-linkedin text-xl"></i></a>
            </div>
          </div>
          <div class="md:col-span-2">
            <h4 class="text-white font-semibold mb-4">平台</h4>
            <ul class="space-y-2">
              <li><a href="#" class="text-gray-400 hover:text-white transition">首页</a></li>
              <li><a href="#" class="text-gray-400 hover:text-white transition">特性</a></li>
              <li><a href="#" class="text-gray-400 hover:text-white transition">文档</a></li>
              <li><a href="#" class="text-gray-400 hover:text-white transition">API</a></li>
            </ul>
          </div>
          <div class="md:col-span-2">
            <h4 class="text-white font-semibold mb-4">资源</h4>
            <ul class="space-y-2">
              <li><a href="#" class="text-gray-400 hover:text-white transition">基因组数据库</a></li>
              <li><a href="#" class="text-gray-400 hover:text-white transition">教程</a></li>
              <li><a href="#" class="text-gray-400 hover:text-white transition">案例分析</a></li>
              <li><a href="#" class="text-gray-400 hover:text-white transition">社区</a></li>
            </ul>
          </div>
          <div class="md:col-span-4">
            <h4 class="text-white font-semibold mb-4">订阅简报</h4>
            <p class="text-sm mb-4">订阅我们的月刊，获取最新的基因组研究进展和平台更新。</p>
            <form class="flex">
              <input type="email" placeholder="您的邮箱" class="flex-grow px-3 py-2 rounded-l-md focus:outline-none focus:ring-2 focus:ring-cyan-500 text-gray-800" />
              <button type="submit" class="px-4 py-2 bg-cyan-500 text-white rounded-r-md hover:bg-cyan-600 transition">
                <i class="fas fa-paper-plane"></i>
              </button>
            </form>
          </div>
        </div>
        <div class="border-t border-gray-700 mt-8 pt-8 text-center text-sm">
          <p>© 2025 转录组分析平台. 保留所有权利.</p>
          <p class="mt-2 text-gray-500" style="font-size:16pt">Copyright 2025，Feeliao/Feelzhou</p>
        </div>
      </div>
    </footer>
  </div>
</template>



<script lang="ts" setup>
import { ref, } from 'vue'
import {Message} from "@element-plus/icons-vue";

const isDark = ref(false)
const toggleDark = () => {
  if (isDark.value) {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
}

const goTo = (url: string) => {
  window.open(url, '_blank')
}

const people = [
  {
    name: '李万峰',
    avatar: '/avatar/liwf.jpg',
    bio: '李万峰，北京大学植物学博士，中国林业科学研究院林业研究所研究员、硕士生导师.\n' +
        '主要研究方向为林木繁育技术与调控、生殖阶段转变以及落叶松等针叶树的分子育种与细胞遗传机制。2009年加入林业研究所，曾在奥地利维也纳农业与科学大学进行博士后研究。\n' +
        '曾主持多个国家级和重大科研项目，在国际林业与植物生物学领域有较高学术影响力。',
    email: 'liwf@caf.ac.cn',
    orcid: 'https://orcid.org/0000-0003-0834-5479',
    github: 'https://github.com/',
  },
  {
    name: '廖堂全',
    avatar: 'https://randomuser.me/api/portraits/women/44.jpg',
    bio: '担任此网站开发的负责人，主要负责项目架构设计和后端代码开发。本科毕业于湖南农业大学，硕士阶段在中国林业科学研究院林业研究所，跟随李万峰老师开展日本落叶松生殖阶段转\n' +
        '变相关研究。对数据分析和可视化充满兴趣，希望能在数据驱动的生物研究中不断探索与创造\n' +
        '价值',
    email: 'lisi@example.com',
    orcid: 'https://orcid.org/0000-0002-3456-7890',
    github: 'https://github.com/lisi',
  },
  {
    name: '周俊杰',
    avatar: 'https://randomuser.me/api/portraits/men/56.jpg',
    bio: '全栈工程师，关注云原生与DevOps。',
    email: 'wangwu@example.com',
    orcid: 'https://orcid.org/0000-0003-4567-8901',
    github: 'https://github.com/wangwu',
  },
]
</script>

<style scoped>
.el-card {
  transition: box-shadow 0.3s;
}
.el-card:hover {
  box-shadow: 0 8px 24px rgba(0,0,0,0.15);
}

</style>
