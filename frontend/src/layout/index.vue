<script setup lang="ts">
import Header from './components/header/index.vue'
// import Aside from './components/aside/index_bak.vue'
import Main from './components/main/index.vue'
import Footer from './components/footer/index.vue'
// import BG from './components/bg/index_bak.vue'
// import { AudioPlayer } from '@/hooks/useAudioPlayer'

// provide('audioPlayer', AudioPlayer())
</script>
<template>
  <!-- <BG /> -->
  <div class="absolute w-full flex flex-col h-full">
    <div
      class="w-full flex flex-col h-full overflow-hidden bg-themeBgColor backdrop-blur-lg"
    >
      <Header />
      <div class="flex flex-1 overflow-hidden">
<!--        <h1>ewewf</h1>-->

<!--        <Aside />-->
        <Main />
      </div>
<!--      <Footer />-->
    </div>
  </div>
</template>
