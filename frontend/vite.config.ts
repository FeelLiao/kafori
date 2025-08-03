import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
// import {fileURLToPath, URL} from "node:url";
import * as path from "node:path";

// https://vite.dev/config/
export default defineConfig({
  server: {
    host: '0.0.0.0',   // 监听所有网卡
    port: 8081         // 端口随意
  },
  plugins: [vue()],
  resolve: {
    // Vite路径别名配置
    alias: {
      '@': path.resolve('./src')
    }
  }

})
