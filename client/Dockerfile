# 构建阶段
FROM node:16-alpine as builder

# 设置工作目录
WORKDIR /app

# 设置 npm 镜像源
RUN npm config set registry https://registry.npmmirror.com && \
    npm config set sass_binary_site https://npmmirror.com/mirrors/node-sass/

# 复制 package.json 和 package-lock.json
COPY package*.json ./

# 安装依赖
RUN npm install

# 复制源代码
COPY . .

# 开发环境配置
ENV NODE_ENV=development

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD wget --spider http://localhost:5173 || exit 1

# 暴露端口
EXPOSE 5173

# 启动命令
CMD ["npm", "run", "dev"] 