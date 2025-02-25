import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import App from './App.vue'
import router from './router'
import pinia from './stores'

const app = createApp(App)

// 全局错误处理
app.config.errorHandler = (err, instance, info) => {
  console.error('应用错误:', {
    error: err,
    component: instance?.$options?.name || '未知组件',
    info,
    time: new Date().toISOString(),
    url: window.location.href
  })
  
  // 可以在这里添加错误上报逻辑
}

// 未捕获的Promise错误处理
window.addEventListener('unhandledrejection', event => {
  console.error('未处理的Promise错误:', {
    error: event.reason,
    time: new Date().toISOString(),
    url: window.location.href
  })
})

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(ElementPlus, {
  locale: zhCn,
})
app.use(router)
app.use(pinia)

app.mount('#app')
