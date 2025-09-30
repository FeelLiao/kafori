import {
  createRouter,
  createWebHistory,
  createWebHashHistory,
  type RouterHistory,
} from 'vue-router'

type RouterMode = 'hash' | 'history'

const mode = (import.meta.env.VITE_ROUTER_MODE || 'history') as RouterMode

const routerMode: Record<RouterMode, () => RouterHistory> = {
  hash: createWebHashHistory,
  history: createWebHistory,
}


const router = createRouter({
  history: routerMode[mode](),
  strict: false,
  scrollBehavior: () => ({ left: 0, top: 0 }),
  routes: [
    {
      path: '/',
      component: () => import('@/views/index.vue'),
    },

    {
      path: '/Transcripts',
      component: () => import('@/views/transcripts/index.vue'),
    },

    {
      path: '/Pipelines',
      component: () => import('@/views/pipelines/index.vue'),
    },

    {
      path: '/Download',
      component: () => import('@/views/download/index.vue'),
    },

    {
      path: '/Tools',
      component: () => import('@/views/tools/index.vue'),
    },

    {
      path: '/Contact',
      component: () => import('@/views/contact/index.vue'),
    },

  ],
})

export default router
