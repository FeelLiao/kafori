import { createApp } from 'vue'
import App from './App.vue'
import router from './routers/index'
import Store from '@/stores'

import zhCn from 'element-plus/es/locale/lang/zh-cn'
import en from 'element-plus/es/locale/lang/en'

import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import ElementPlus from 'element-plus'

import '@/assets/css/tailwind.css'  // 确保引入路径正确

import "@pureadmin/table/dist/style.css";
import PureTable from "@pureadmin/table";


import VueECharts from 'vue-echarts'
import 'echarts' // 只需要安装，不需要手动import

import i18n from '@/i18n';

let config = {
    DEV_BASE_URL: 'http://localhost:8081', // 默认值
    PRO_BASE_URL: 'http://192.168.80.51:8080'
};



const app = createApp(App)

// const pinia = createPinia();
//
// pinia.use(piniaPluginPersistedstate({
//     // 配置选项
// }));


app.config.globalProperties.$config = config;

// app.use(pinia);
// 路由
app.use(router)
// 状态管理
app.use(Store)
// ElementPlus

const elementLocales = { zh: zhCn, en: en }
const locale = localStorage.getItem('lang') || 'en'
app.use(i18n);

app.use(ElementPlus, { locale: i18n.global.locale })



app.use(PureTable, { locale: i18n.global.locale })


app.component('v-chart', VueECharts)

app.mount('#app')
