import { createRouter, createWebHistory } from 'vue-router'
import UploadPages from '@/components/UploadPages.vue'
import ViewPages from '@/components/ViewPages.vue'
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/view_pages',
      name: "view_pages",
      component: ViewPages
    },
    {
      path: '/upload_pages',
      name: "upload_pages",
      component: UploadPages
    }
  ]
})

export default router
