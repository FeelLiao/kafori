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
      <div class="text-sm mb-4 text-gray-500 dark:text-gray-300 text-center px-2">{{ person.introduction }}</div>
      <div
          class="flex gap-6 justify-center items-center absolute left-0 right-0 bottom-6"
      >
        <el-tooltip v-if="person.email" content="Email" placement="top">
          <el-icon
              class="cursor-pointer"
              style="font-size:45px;display:flex;align-items:center;justify-content:center;"
              @click="goTo(`mailto:${person.email}`)"
          >
            <Message />
          </el-icon>
        </el-tooltip>
        <el-tooltip v-if="person.orcid" content="Orcid" placement="top">
          <img
              src="/icon/orcid.svg"
              alt="ORCID"
              class="cursor-pointer"
              style="width:48px;height:48px;object-fit:contain;display:flex;align-items:center;justify-content:center;"
              @click="goTo(person.orcid)"
          />
        </el-tooltip>
        <el-tooltip v-if="person.github" content="Github" placement="top">
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
      <h2 class="text-2xl font-bold mb-4 text-gray-800 dark:text-gray-100">{{$t('Contact_team')}}</h2>
      <p class="mb-4 text-gray-600 dark:text-gray-300">
        {{$t('Contact_team_desc')}}
      </p>
      
    </div>
    <footer class="bg-gray-800 dark:bg-gray-900 text-gray-300 py-12">
      <div class="container mx-auto px-4">
        <div class="grid grid-cols-1 md:grid-cols-12 gap-8">
          <div class="md:col-span-4">
            <div class="flex items-center space-x-2 mb-4">
              <div class="w-8 h-8 rounded-full bg-gradient-to-br from-lime-400 to-cyan-400 dark:from-lime-700 dark:to-cyan-700"></div>
              <span class="text-xl font-bold text-white">{{$t('footer_analytics')}}</span>
            </div>
            <p class="text-sm">{{$t('footer_desc')}}</p>
            <div class="flex space-x-4 mt-4">
              <a href="#" class="text-gray-400 hover:text-white transition"><i class="fab fa-github text-xl"></i></a>
              <a href="#" class="text-gray-400 hover:text-white transition"><i class="fab fa-twitter text-xl"></i></a>
              <a href="#" class="text-gray-400 hover:text-white transition"><i class="fab fa-linkedin text-xl"></i></a>
            </div>
          </div>
          <div class="md:col-span-2">
            <h4 class="text-white font-semibold mb-4">{{$t('footer_platform')}}</h4>
            <ul class="space-y-2">
              <li><router-link to="/" class="text-gray-400 hover:text-white transition">{{$t('nav_Home')}}</router-link></li>
              <li><router-link to="/Transcripts" class="text-gray-400 hover:text-white transition">{{$t('nav_Transcripts')}}</router-link></li>

            </ul>
          </div>
          <div class="md:col-span-2">
            <h4 class="text-white font-semibold mb-4">{{$t('footer_resource')}}</h4>
            <ul class="space-y-2">
              <li><router-link to="/Download" class="text-gray-400 hover:text-white transition">{{$t('nav_Download')}}</router-link></li>
              <li><router-link to="/Help" class="text-gray-400 hover:text-white transition">{{$t('nav_Help')}}</router-link></li>
            </ul>
          </div>
          <div class="md:col-span-4">
            <h4 class="text-white font-semibold mb-4">{{$t('footer_support')}}</h4>
            <p class="text-sm mb-4">{{$t('footer_support_desc')}}</p>

          </div>
        </div>
        <div class="border-t border-gray-700 mt-8 pt-8 text-center text-sm">
          <p>{{$t('footer_copy')}}</p>
          <p class="mt-2 text-gray-500" style="font-size:16pt">{{$t('footer_copy_txt')}}</p>
        </div>
      </div>
    </footer>
  </div>
</template>



<script lang="ts" setup>
import {computed, ref,} from 'vue'
import {Message} from "@element-plus/icons-vue";
import i18n from '@/i18n/index.ts'


const goTo = (url: string) => {
  window.open(url, '_blank')
}

const people = computed(() => [
  {
    name: i18n.global.t('Contact_lwf_name'),
    avatar: '/avatar/lwf.jpg',
    introduction: i18n.global.t('Contact_lwf_introduction'),
    email: 'liwf@caf.ac.cn',
    orcid: 'https://orcid.org/0000-0003-0834-5479',
  },
  {
    name: i18n.global.t('Contact_ltq_name'),
    avatar: '/avatar/ltq.jpg',
    introduction: i18n.global.t('Contact_ltq_introduction'),
    email: 'feelteel@hotmail.com',
    orcid: 'https://orcid.org/0009-0001-6764-7226',
    github: 'https://github.com/FeelLiao',
  },
  {
    name: i18n.global.t('Contact_zjj_name'),
    avatar: '/avatar/zjj.jpg',
    introduction: i18n.global.t('Contact_zjj_introduction'),
    email: 'feelzhou2004@163.com',
    github: 'https://github.com/zhou2004',
  },
]);
</script>

<style scoped>
.el-card {
  transition: box-shadow 0.3s;
}
.el-card:hover {
  box-shadow: 0 8px 24px rgba(0,0,0,0.15);
}

</style>
