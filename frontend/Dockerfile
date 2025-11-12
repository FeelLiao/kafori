# 1) 前端构建阶段（Node 22.14.0）
FROM node:22.14.0 AS frontend-build

# 可选：国内 npm 源（默认用 npmmirror，可在构建时覆盖）
ARG NPM_REGISTRY=https://registry.npmmirror.com
RUN if [ -n "$NPM_REGISTRY" ]; then npm config set registry "$NPM_REGISTRY"; fi

# 复制前端代码
COPY ./frontend /app

# 定位到前端工作目录
WORKDIR /app/

# 使用npm并开始构建
RUN --mount=type=cache,target=/root/.npm \
    npm install && npm run build

# 设置构建目录的参数
ARG FRONTEND_BUILD_DIR=dist


# 2) Nginx 运行阶段（Nginx 1.27）
FROM nginx:1.27 AS runtime

# 拷贝前端打包产物到 Nginx 静态目录
COPY --from=frontend-build /app/${FRONTEND_BUILD_DIR}/ /usr/share/nginx/html/


EXPOSE 80
EXPOSE 443
CMD ["nginx","-g","daemon off;"]