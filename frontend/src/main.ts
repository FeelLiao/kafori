import { createApp } from 'vue'
import App from './App.vue'
import router from './routers/index'
import Store from '@/stores'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import '@/style/index.scss'

let config = {
    DEV_BASE_URL: 'http://localhost:8081', // 默认值
    PRO_BASE_URL: 'http://192.168.80.51:8080'
};



const app = createApp(App)

app.config.globalProperties.$config = config;

// 路由
app.use(router)
// 状态管理
app.use(Store)
// ElementPlus
app.use(ElementPlus, {
    locale: zhCn,
})
app.mount('#app')
