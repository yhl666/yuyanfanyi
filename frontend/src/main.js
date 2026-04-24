import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import './style.css'

// 动态导入组件
import Home from './Home.vue'
import Test from './Test.vue'
import History from './History.vue'

// 创建路由
const routes = [
  { path: '/', component: Home },
  { path: '/test', component: Test },
  { path: '/history', component: History }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 创建根组件
import RootApp from './RootApp.vue'

const app = createApp(RootApp)
app.use(router)
app.mount('#app')
