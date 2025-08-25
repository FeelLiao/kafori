<template>
  <el-card shadow="always">
    <div style="margin-bottom: 18px;">
      <el-upload
          :action="uploadUrl"
          :show-file-list="false"
          :on-success="handleUploadSuccess"
          :before-upload="beforeUpload"
      >
        <el-button type="primary" icon="el-icon-upload">上传文件</el-button>
      </el-upload>
    </div>
    <el-table :data="fileList" style="width: 100%">
      <el-table-column prop="name" label="文件名" />
      <el-table-column prop="size" label="大小" width="120" />
      <el-table-column label="操作" width="130">
        <template #default="scope">
          <el-button
              type="success"
              size="small"
              @click="downloadFile(scope.row)"
              icon="el-icon-download"
          >下载</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup>
import {ref} from 'vue'

// 模拟文件列表
const fileList = ref([
  {name: 'example1.pdf', size: '1.2MB', url: '/mock/example1.pdf'},
  {name: 'image.png', size: '800KB', url: '/mock/image.png'},
])

// 上传接口（此处用 mock，实际项目请替换为真实接口地址）
const uploadUrl = '/mock/upload'

// 上传前校验
function beforeUpload(file) {
  // 可以做大小、类型校验
  // return false 可阻止上传
  return true
}

// 上传成功后，添加到列表
function handleUploadSuccess(response, file) {
  // response 根据后端返回，假设直接返回url
  fileList.value.push({
    name: file.name,
    size: (file.size / 1024).toFixed(2) + 'KB',
    url: response.url || '/mock/' + file.name
  })
}

// 下载文件（此处模拟，实际项目可用window.open或a标签下载）
function downloadFile(file) {
  // 真实项目可直接 window.open(file.url)
  // 这里模拟下载逻辑
  const link = document.createElement('a')
  link.href = file.url
  link.download = file.name
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}
</script>

<style scoped>
.el-card {
  max-width: 600px;
  margin: 30px auto;
}
</style>