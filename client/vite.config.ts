import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vite.dev/config/

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  },
  build: {
    // 优化构建配置
    chunkSizeWarningLimit: 2000,
    rollupOptions: {
      output: {
        manualChunks: {
          'element-plus': ['element-plus'],
          'echarts': ['echarts'],
          'xlsx': ['xlsx', 'file-saver']
        }
      }
    }
  },
  server: {
    // 限制内存使用
    hmr: {
      overlay: false
    },
    watch: {
      usePolling: false
    },
    // 添加内存限制
    fs: {
      strict: true
    }
  },
  // 优化依赖预构建
  optimizeDeps: {
    include: ['xlsx', 'file-saver']
  }
})
