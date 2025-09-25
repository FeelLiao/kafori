import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import VueI18nPlugin from '@intlify/unplugin-vue-i18n/vite'
import * as path from "node:path";

export default defineConfig({
  server: {
    host: '0.0.0.0',   // 监听所有网卡
    port: 8081,         // 端口随意
    proxy: {
      '/register': 'http://192.168.80.51:5000',
      '/login': 'http://192.168.80.77/api',
      '/profile': 'http://192.168.80.77/api'
    }
  },
  plugins: [
      vue(),
    VueI18nPlugin({ runtimeOnly: false })
  ],
  resolve: {
    // Vite路径别名配置
    alias: {
      '@': path.resolve('./src')
    }
  }

})
