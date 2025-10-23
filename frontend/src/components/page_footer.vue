<script setup lang="ts">

</script>

<template>
  <footer class="flex items-center justify-between bg-gray-800 dark:bg-gray-900 text-gray-300 py-12">
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

      </div>
    </div>
  </footer>
</template>

<style scoped>

</style>