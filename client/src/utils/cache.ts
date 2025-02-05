interface CacheItem<T> {
  data: T
  timestamp: number
  expireAt: number
}

class Cache {
  private storage: Map<string, CacheItem<any>>
  private readonly defaultTTL: number

  constructor(defaultTTL = 5 * 60 * 1000) { // 默认5分钟
    this.storage = new Map()
    this.defaultTTL = defaultTTL
  }

  set<T>(key: string, data: T, ttl?: number): void {
    const timestamp = Date.now()
    const expireAt = timestamp + (ttl || this.defaultTTL)
    
    this.storage.set(key, {
      data,
      timestamp,
      expireAt
    })
  }

  get<T>(key: string): T | null {
    const item = this.storage.get(key)
    
    if (!item) {
      return null
    }

    if (Date.now() > item.expireAt) {
      this.storage.delete(key)
      return null
    }

    return item.data as T
  }

  has(key: string): boolean {
    return this.get(key) !== null
  }

  delete(key: string): void {
    this.storage.delete(key)
  }

  clear(): void {
    this.storage.clear()
  }

  // 清理过期缓存
  cleanup(): void {
    const now = Date.now()
    for (const [key, item] of this.storage.entries()) {
      if (now > item.expireAt) {
        this.storage.delete(key)
      }
    }
  }
}

// 创建全局缓存实例
export const cache = new Cache()

// 定期清理过期缓存
setInterval(() => {
  cache.cleanup()
}, 60 * 1000) // 每分钟清理一次 