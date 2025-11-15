import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import TranslationExerciseView from '../views/TranslationExerciseView.vue'
import TemplateBuilderView from '../views/TemplateBuilderView.vue'
import SavedTemplatesView from '../views/SavedTemplatesView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/exercise/translation',
      name: 'translation',
      component: TranslationExerciseView
    },
    {
      path: '/builder',
      name: 'builder',
      component: TemplateBuilderView
    },
    {
      path: '/templates',
      name: 'templates',
      component: SavedTemplatesView
    }
  ]
})

export default router
