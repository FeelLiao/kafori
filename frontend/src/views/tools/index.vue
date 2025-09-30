<template>
  <div class="v2-embed-container">
    <iframe
        :src="sequence_server"
        style="width:100%; height:100vh; border:none;"
    ></iframe>
  </div>
</template>

<script lang="ts" setup>
const sequence_server = import.meta.env.VITE_SEQUENCE_SERVER
</script>