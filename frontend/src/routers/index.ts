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
      component: () => import('@/pages/index.vue'),
    },

    {
      path: '/Transcripts',
      component: () => import('@/pages/transcripts/index.vue'),
    },

    {
      path: '/Pipelines',
      component: () => import('@/pages/pipelines/index.vue'),
    },

    {
      path: '/Download',
      component: () => import('@/pages/download/index.vue'),
    },

    {
      path: '/Tools',
      component: () => import('@/pages/tools/index.vue'),
    },

    {
      path: '/Contact',
      component: () => import('@/pages/contact/index.vue'),
    },

  ],
})

export default router
