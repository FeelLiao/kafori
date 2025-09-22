# kafori 文档总览

本文档目录为项目文档的入口索引，帮助你快速定位到常用指南、API 文档、插件开发、数据与部署说明等内容。

## 快速导航

- 后端 API 文档
  - [API 接口设计](./后端API文档/API接口设计.md)
  - [拓展插件集成](./后端API文档/拓展插件集成.md)
  - [数据处理流程](./后端API文档/数据处理流程.md)
  - [数据库设计](./后端API文档/数据库设计.md)
- 部署指南（Linux / Docker）
  - [1-Linux 安装 MySQL 8.0.22（基于 Debian12）](./部署/1-Linux安装MySQL8.0.22（基于Debian12）.md)
  - [2-Linux 源码安装 Redis](./部署/2-Linux源码安装redis.md)
  - [Docker 安装（Debian12）](./部署/docker安装(debian12).md)
- 其他
  - [FastAPI 基础](./fastapi基础.md)
  - [贡献指南（CONTRIBUTING）](./CONTRIBUTING.md)

## 文档适用对象
- 平台使用者：了解可用 API、数据流程与部署环境
- 平台开发者：扩展后端分析/下载插件、维护数据库结构、改进部署与运维

## 技术栈概览
- 后端：FastAPI（Python）
- 分析计算：R（通过 rpy2 与多进程池集成）；内置 PCA、差异分析（edgeR/limma）等示例
- 数据库：MySQL（参考部署文档），Redis（缓存/队列）
- 前端：Vue 3 + Vite（见仓库 `frontend/`）
- 容器化：Docker（见 `docker/` 与部署文档）

## API 约定与调试入口
- 统一返回包装：`{ code: 0|1, message: string, data: any|null }`
  - 成功：`code=0`
  - 失败：`code=1`（部分异常也可能使用框架默认 HTTP 错误结构，详见 API 文档）
- 文档与调试：FastAPI 通常提供 Swagger UI（`/docs`）与 ReDoc（`/redoc`），具体以实际部署路由为准

## 推荐阅读顺序
1. [API 接口设计](./后端API文档/API接口设计.md)：了解接口分组、请求/响应示例与错误约定
2. [拓展插件集成](./后端API文档/拓展插件集成.md)：扩展“分析插件”和“下载数据源插件”的最佳实践与示例代码
3. [数据处理流程](./后端API文档/数据处理流程.md)：数据从上传、校验、入库到分析的全流程
4. [数据库设计](./后端API文档/数据库设计.md)：表结构、主外键关系与索引建议
5. 部署相关文档：按需选择 MySQL、Redis、Docker 的安装与配置

## 目录结构（docs/）
```
CONTRIBUTING.md
fastapi基础.md
README.MD  ← 本文件
后端API文档/
  ├─ API接口设计.md
  ├─ README.md
  ├─ 拓展插件集成.md
  ├─ 数据处理流程.md
  └─ 数据库设计.md
部署/
  ├─ 1-Linux安装MySQL8.0.22（基于Debian12）.md
  ├─ 2-Linux源码安装redis.md
  └─ docker安装(debian12).md
```

## 维护与贡献
- 贡献流程与规范见：[CONTRIBUTING.md](./CONTRIBUTING.md)
- 提交 PR 前请确保：
  - 新增/修改的 API 已在“API 接口设计”中同步更新
  - 插件新增/接口变更已在“拓展插件集成”与“数据处理流程”中补充说明
  - 如涉及部署或配置变更，请同步更新“部署”相关文档

---
最后更新：2025-09-22
