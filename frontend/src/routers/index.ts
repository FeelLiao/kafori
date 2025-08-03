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
      path: '/table',
      component: () => import('@/pages/table/index.vue'),
    },
    {
      path: '/download',
      component: () => import('@/pages/download/index.vue'),
    },

  ],
})

export default router
