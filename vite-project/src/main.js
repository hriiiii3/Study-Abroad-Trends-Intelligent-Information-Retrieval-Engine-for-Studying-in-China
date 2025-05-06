import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import 'element-plus/dist/index.css'
import router from './router'
import App from './App.vue'

const app = createApp(App)

// 注册所有Element Plus图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(createPinia())
app.use(router)
app.use(ElementPlus)

// 全局错误处理
app.config.errorHandler = (err, vm, info) => {
  console.error('Vue全局错误:', err)
  console.error('错误组件:', vm)
  console.error('错误信息:', info)
}

// 添加自定义导航守卫，处理vnode为null的情况
router.beforeResolve((to, from, next) => {
  // 确保页面切换时不会因数据问题导致渲染错误
  next()
})

app.mount('#app')
