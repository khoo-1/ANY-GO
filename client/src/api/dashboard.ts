import request from '@/utils/request'

// 仪表盘API接口
export default {
  // 获取统计数据
  getStatistics() {
    return request.get('/api/dashboard/statistics')
  },

  // 获取趋势数据
  getTrends() {
    return request.get('/api/dashboard/trends')
  }
} 