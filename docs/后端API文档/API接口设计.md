# API接口设计

kafori日本落叶松转录组数据库及分析平台后端API接口设计文档。

后端API的定义在`backend/routers`文件夹，主要包括以下几个模块：

1. `analysis_routers.py`：与转录组数据分析相关的API接口，用于用户筛选转录组数据后的自定义分析
2. `db_routers.py`：与读取数据库相关的API接口，用于前端页面展示数据库中的数据
3. `download_routers.py`：与文件下载相关的API接口，用于用户下载数据库中的数据
4. `file_routers.py`：与用户上传文件相关的API接口，用于用户上传数据到数据库中
5. `routers.py`：与路由相关的API接口，用于处理不同API请求的路由分发
6. `validation.py`：与请求参数验证相关的API接口，用于对部分API接口做验证，仅允许特定用户访问

## `analysis_routers`分析相关接口

该模块提供用户自定义分析的API接口。用户通过前端页面选择样本与基因后，调用这些接口运行预定义的R分析插件（如PCA、差异分析等），并返回结果供前端展示。

该接口可以通过插件机制灵活扩展新的分析功能。每个分析插件需实现特定接口并注册到系统中，后端通过统一的调用方式运行，详细接入方式见 [拓展插件集成](拓展插件集成.md)。
 
### 1. 获取分析目录

- 接口路径: GET /transcripts/analysis/catalog
- 功能: 列出已注册的分析插件及其参数 JSON Schema，前端可据此动态渲染参数表单
- 权限: 公开

成功响应示例:
```json
{
  "code": 0,
  "message": "OK",
  "data": [
    {
      "id": "pca",
      "title": "PCA",
      "input_type": "tpm",
      "params_schema": {
        "type": "object",
        "properties": {
          "title": "PCAParams",
          "type": "object",
          "width": {
            "default": 800,
            "description": "Plot width in px",
            "title": "Width",
            "type": "integer"
          },
          "height": {
            "default": 600,
            "description": "Plot height in px",
            "title": "Height",
            "type": "integer"
          },
          // 具体取决于插件定义，可能还有其它参数
        },
      }
    }
  ]
}
```

失败响应:
- 500 服务器内部错误
```json
{ "code": 1, "message": "Internal Server Error", "data": null }
```

返回字段说明:
- id: 分析唯一标识（**与后续运行接口的 analysis 字段一致**）
- title: 分析名称
- input_type: 插件需要的数据类型（tpm/counts），在运行分析中这一字段不需要前端指定，后端会自动处理。
- params_schema: 该分析参数的 JSON Schema（由 Pydantic 模型生成）



### 2. 运行分析

- 接口路径: POST /transcripts/analysis
- 功能: 运行指定的分析插件；后端从数据库按 input_type 抓取数据，调用 R 分析并返回结果
- 权限: 公开
- Content-Type: application/json

请求体字段:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| analysis | string | 是 | 分析ID（需与目录接口返回的 id 匹配，如 pca） |
| params | object | 否 | 分析参数，结构由catalog接口的 params_schema 定义（如 width、height 等） |
| data_filter | object | 是 | 数据筛选条件 |

data_filter 子字段:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| unique_id | array(string) | 是 | 样本 UniqueEXID 列表 |
| gene_name | array(string) | 否 | 基因ID列表；当 all_gene=true 时可留空 [] |
| all_gene | boolean | 否 | 是否忽略 gene_name 并返回全部基因（默认 false） |

请求示例:
```json
{
  "analysis": "pca",
  "params": { "width": 900, "height": 600 },
  "data_filter": {
    "unique_id": ["LRX68bc3ebb001","LRX68bc3ebb002","LRX68bc3ebb003","LRX68bc3ebb004"],
    "gene_name": [],
    "all_gene": true
  }
}
```

成功响应示例（不同插件返回结构会有所差异，以下为 PCA 示例）:
```json
{
  "code": 0,
  "message": "OK",
  "data": {
    "meta": { "title": "PCA" },
    "plots": [
      { "format": "image/svg+xml;base64", "title": "PCA Plot", "data": "<base64-encoded-svg>" }
    ],
    "tables": {
      "pca_eig": [ { "PC": "Dim.1", "Variance": 42.1, "Cumulative": 42.1 }, { "PC": "Dim.2", "Variance": 21.3, "Cumulative": 63.4 } ],
      "pca_sample": [ { "Sample": "LRX68bc3ebb001", "Dim.1": 1.23, "Dim.2": -0.45, "group": "LRX68bc3ebb001" } ]
    }
  }
}
```

失败响应:
- 404 未知分析ID
```json
{ "detail": "Unknown analysis: <analysis>" }
```
- 500 分析执行失败（R 运行错误或数据为空等）
```json
{ "code": 1, "message": "Analysis failed: <error message>", "data": null }
```

参数与逻辑说明:
- 插件机制: 后端通过注册表按 analysis 字段获取插件类（get_analysis），实例化并执行 plugin.run()。
- 数据抓取: 根据插件声明的 input_type（tpm/counts）从数据库获取长表，转换为宽表后传入插件。
- 参数校验: params 由插件声明的 Pydantic Params 模型校验（超出 schema 的字段将被拒绝或忽略，视实现而定）。
- 返回结构: 插件返回统一结构：
  - meta: 元信息（如标题）
  - plots: 图像数组（格式字段如 image/svg+xml;base64；data 为 base64 内容）
  - tables: 各分析表结果（DataFrame 转 records）
- 性能与超时: 后端在单独进程运行 R 代码，默认 60s 超时与重试（见 analysis_base.RProcessorPool* 实现）；大量样本/基因时建议前端限制筛选范围或后台化处理。

错误场景总结:
| 场景 | 触发 | 返回 |
|------|------|------|
| analysis 不存在 | 未注册的插件ID | 404 |
| 数据为空 | unique_id/gene_name 过滤后无数据 | 500（后续可细化为 404） |
| R 运行错误 | R 包缺失/参数非法/输入非数值 | 500 |
| 参数非法 | 不符合 params_schema | 400（由 Pydantic 抛出；当前实现捕获后以 500 形式返回） |



## `db_routers`数据库相关接口

该模块提供访问转录组数据库的API接口，供前端页面展示数据库中的数据。主要包括按条件查询样本信息与获取样本统计信息等功能。

### 1. 查询转录组数据库接口

- 接口路径: `POST /transcripts/query`
- 功能: 按类型查询实验类别 / 实验名称 / 样本信息
- 权限: 公开

请求体字段:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| query_type | string | 是 | 查询类型: `exp_class` / `exp_name` / `sample_id` |
| query_value | tuple(array) | 条件必填 | 当 query_type = `exp_name` 或 `sample_id` 时必填；`exp_class` 可省略 |

query_type 取值说明:
- exp_class: 返回全部实验类别 (ExpClass, ExperimentCategory)
- exp_name: 根据实验类别名称ID过滤 (传入ExpClass元组/数组)
- sample_id: 根据实验名称ID过滤 (传入UniqueEXID元组/数组)

请求示例:
```json
{ "query_type": "exp_class" }
```
```json
{ "query_type": "exp_name", "query_value": ["EXPC68b567d3001"] }
```
```json
{ "query_type": "sample_id", "query_value": ["TRCRIE68b567d3002"] }
```

成功响应, data字段根据query_type变化:
```json
{
  "code": 0,
  "message": "success",
  "data": [
    { "ExpClass": "ClassA", "ExperimentCategory": "Cat1" }
  ]
}
```

失败响应:
- 400 参数校验失败 (例如缺少必须的 query_value)
```json
{
  "detail": [
    {
      "type": "value_error",
      "msg": "query_value is required when query_type is exp_name or sample_id",
      "loc": ["body","query_value"]
    }
  ]
}
```
- 404 无结果
```json
{ "detail": "No data found" }
```

返回字段说明:
| 字段 | 说明 |
|------|------|
| code | 0 成功；1 失败（当前实现失败走异常 HTTP 状态码） |
| message | 执行结果信息 |
| data | 结果列表；字段随查询类型变化 |

参数与逻辑说明:
- 校验: 当 query_type ∈ {exp_name, sample_id} 且未提供 query_value -> 直接校验失败
- 空结果: 返回 404
- 成功: DataFrame 转换为 records 列表

错误场景总结:
| 场景 | 触发 | 返回 |
|------|------|------|
| 缺少 query_value | exp_name/sample_id 且未传 | 400 校验错误 |
| 无匹配数据 | 查询结果为空 | 404 |
| 其他异常 | 运行期错误 | 500 (可后续统一处理) |

### 2. 转录组数据库样本统计信息查询接口

- 接口路径: `POST /transcripts/get_allexp_counts`
- 功能: 获取所有样本的实验类别及其对应的样本数量
- 权限: 公开

> [!WARNING]
> 该接口目前尚处于开发阶段，返回的结果仅供前端页面开发使用，后续可能会调整。

后续调整方向: 将数据库查询结果统计后按天存储在 Redis 中，前端直接读取 Redis 结果，避免每次请求都查询数据库。

## `download_routers`下载相关接口

该模块提供文件下载相关的API接口，供用户下载配置文件和数据库中的数据。主要包括下载物种基因组文件和数据库中的样本信息表及表达量信息表等功能。

该接口可以通过插件机制灵活扩展新的下载功能。每个下载插件需实现特定接口并注册到系统中，后端通过统一的调用方式运行，详细接入方式见 [拓展插件集成](拓展插件集成.md)。

### 1. 下载目录查询

- 接口路径: GET /download/catalog
- 功能: 获取可下载资源的目录树（各类资源及其可下载文件列表），供前端渲染
- 权限: 公开

成功响应示例:
```json
{
  "code": 0,
  "message": "Success",
  "data": [
    {
      "classes": "Genomic Data",
      "items": {
        "genome_fasta": {
          "filename": "Larix_reference.fa.gz",
          "media_type": "application/gzip"
        },
        "genome_annotation": {
          "filename": "Larix_annotation.gtf.gz",
          "media_type": "application/gzip"
        }
      }
    }
  ]
}
```

失败响应:
```json
{ "code": 1, "message": "Internal error message", "data": null }
```

说明:
- data 为数组，每个元素代表一个下载类别，包含字段：
  - `classes`: 类别名称（由后端注册，例：`Genomic Data`）
  - `items`: 该类别下的条目字典，键为条目标识（例如 `genome_fasta`），值为包含以下字段的对象：
    - `filename`: 实际文件名（用于下载路径）
    - `media_type`: MIME 类型（由后端使用 `mimetypes` 推断）
- 安全考虑：目录中不返回服务器文件的物理 `path`，仅提供 `filename` 与 `media_type`。
- 可通过注册更多提供者扩展下载类别；前端无需改动逻辑，只需渲染本接口返回的数据。

### 2. 下载文件

- 接口路径: POST /download/{classes}/{filename}
- 功能: 下载指定类别下的目标文件
- 权限: 公开
- 路径参数:
  - `classes` string 必填 资源类别（需与目录接口返回的 `classes` 字段匹配；如包含空格请进行 URL 编码）
  - `filename` string 必填 文件名（需与目录接口返回的 `items[*].filename` 匹配）
- 请求体: 无

请求示例:
```bash
curl -X POST "http://localhost:8000/download/Genomic%20Data/Larix_reference.fa.gz" -o Larix_reference.fa.gz
```

成功响应:
- 直接返回二进制文件数据
- 常见响应头:
  - `Content-Type`: 与目录中 `media_type` 一致（推断失败时为 `application/octet-stream`）
  - `Content-Disposition`: `attachment; filename="Larix_reference.fa.gz"`

失败响应:
```json
{ "code": 1, "message": "Unknown download provider: <classes>", "data": null }
```
```json
{ "code": 1, "message": "Unknown filename: <filename>", "data": null }
```
```json
{ "code": 1, "message": "File not found: <path>", "data": null }
```

说明:
- 当前实现下，无论成功或失败均返回 HTTP 200；失败时以统一 JSON 结构 `{code,message,data}` 表达错误。
- `classes` 未注册或 `filename` 不存在时，将返回如上错误结构；请仅从“下载目录查询”接口返回的数据发起下载以避免无效请求。

## `file_routers`上传文件接口


本模块用于上传样本信息表与基因表达矩阵，并在全部数据校验通过后一次性写入数据库。Redis 作为临时缓存（每份数据 TTL: 600 秒）。数据提交有两种方式：

1. 样本信息文件 xlsx + 基因表达矩阵 tpm counts（两个csv文件）**已实现**
2. 样本信息文件 xlsx + 原始测序数据 **已实现**

改进方向:
- 前端在每一步成功后提示剩余有效时间 (600s)
- 入库前可增加一个检查接口用于确认三份缓存是否存在 (后续扩展)

通用说明:
- 认证: 所有接口均需 Bearer Token（`Authorization: Bearer <token>`），来源于登录接口
- 返回结构统一使用:
  成功: { "code": 0, "message": "<成功消息>", "data": null }
  失败: { "code": 1, "message": "<失败原因>", "data": null }
- 失败也使用 HTTP 200（当前实现方式），仅 message / code 区分
- 临时缓存键:
  {user}_sample_sheet
  {user}_gene_tpm
  {user}_gene_counts

### 1. 上传样本信息表

- 接口路径: POST /pipeline/sample_sheet/
- 功能: 上传并校验样本信息 Excel；缓存为 parquet 到 Redis
- Content-Type: multipart/form-data
- 权限: 需登录

请求参数 (Form):
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | file(xlsx) | 是 | 样本信息表，Excel，包含 SampleInfo sheet |

成功响应:
```json
{ "code": 0, "message": "Sample sheet uploaded successfully.", "data": null }
```

失败响应示例:
```json
{ "code": 1, "message": "Sample sheet uploaded failed.", "data": null }
```

### 2. 上传基因表达 TPM 矩阵

- 接口路径: POST /pipeline/gene_ex_tpm/
- 功能: 上传 TPM 表 (CSV) 并校验与已缓存样本表一致（SampleID 匹配等）
- 前置条件: 已成功上传样本信息表
- Content-Type: multipart/form-data
- 权限: 需登录

请求参数:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | file(csv) | 是 | 基因表达 TPM 文件 |

成功响应:
```json
{ "code": 0, "message": "Gene expression data GeneDataType.tpm uploaded successfully.", "data": null }
```

可能失败:
- 未先上传样本表 -> 读取 Redis 为空
- SampleID 不匹配 / 行列格式错误
```json
{ "code": 1, "message": "SampleID mismatch: A-1 not found in sample sheet", "data": null }
```

### 3. 上传基因表达 Counts 矩阵

- 接口路径: POST /pipeline/gene_ex_counts/
- 功能: 上传 Counts 表 (CSV) 并校验
- 前置条件: 样本表已上传
- Content-Type: multipart/form-data
- 权限: 需登录

请求参数:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | file(csv) | 是 | 基因表达 TPM 文件 |

成功响应:
```json
{ "code": 0, "message": "Gene expression data GeneDataType.counts uploaded successfully.", "data": null }
```

失败示例:
```json
{ "code": 1, "message": "Gene expression data validation failed: duplicate gene_id", "data": null }
```

### 4. 原始测序数据直传（分步上传原始文件）

- 接口路径: PUT /pipeline/rawdata_upload
- 功能: 以 application/octet-stream 方式将原始测序文件直接上传到服务端（按用户隔离目录存储）
- 权限: 需登录
- Content-Type: application/octet-stream

请求参数:
- Query
  - filename string 必填 要保存的目标文件名（例如 SRR001_1.fq.gz）
- Header
  - Content-Length integer 可选 文件总长度（用于校验）

请求体:
- 二进制文件流（octet-stream）

请求示例 (Linux):
```bash
curl -X PUT \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/octet-stream" \
  -T SRR001_1.fq.gz \
  "http://localhost:8000/pipeline/rawdata_upload?filename=SRR001_1.fq.gz"
```

成功响应:
```json
{ "code": 0, "message": "File uploaded successfully", "data": { "filename": "SRR001_1.fq.gz", "size": 123456789 } }
```

失败响应（示例）:
```json
{ "code": 1, "message": "Content-Type must be application/octet-stream", "data": null }
```
```json
{ "code": 1, "message": "Target file already exists: SRR001_1.fq.gz", "data": null }
```
```json
{ "code": 1, "message": "Content-Length mismatch: got=123, expected=456", "data": null }
```
客户端断开:
```json
{ "detail": "Client Closed Request" }  // HTTP 499
```

说明:
- 服务端先写入临时 .part 文件并在完成后原子落盘，避免部分写入。
- 若配置了最大体积 MAX_BYTES，超过将拒绝（当前默认为无限制）。


### 5. 原始文件 MD5 校验

- 接口路径: POST /pipeline/rawdata_md5_check/
- 功能: 根据已上传的样本信息表，从用户目录读取原始文件并进行 MD5 校验；返回未通过校验的文件列表
- 权限: 需登录
- 前置条件: 已成功上传样本信息表（缓存于 Redis）

请求体: 无

成功响应:
```json
{ "code": 0, "message": "All upload rawdata files MD5 check passed.", "data": null }
```

失败响应:
```json
{
  "code": 1,
  "message": "Some of the upload rawdata files MD5 check failed.",
  "data": { "invalid_files": ["SRR001_1.fq.gz","SRR001_2.fq.gz"] }
}
```

说明:
- 校验依据由后端根据样本表与用户原始文件目录匹配得到。样本表需包含原始文件标识与MD5信息（具体列以实现为准）。


### 6. 触发上游处理流程（比对与定量）

- 接口路径: POST /pipeline/rawdata_processing/
- 功能: 使用样本表与用户上传的原始数据启动上游转录组流水线（如比对、质控、定量）；先进行 dry-run 校验，通过后后台运行
- 权限: 需登录
- 前置条件:
  - 样本信息表已上传并缓存
  - 原始数据文件已上传且通过 MD5 校验

请求体: 无

成功响应（dry-run 通过，后台已启动）:
```json
{ "code": 0, "message": "Dry run passed. Upstream analysis is running in background.", "data": null }
```

失败响应（dry-run 未通过）:
```json
{ "code": 1, "message": "Dry run failed. Please see log for more information.", "data": null }
```

说明:
- 运行状态会写入 Redis 键 {user}_upstream_status，可通过状态接口查询。
- 资源参数（线程数、参考基因组/注释等）由后端配置管理。


### 7. 上游处理状态查询

- 接口路径: POST /pipeline/rawdata_status/
- 功能: 查询上游处理当前状态
- 权限: 需登录
- 请求体: 无

成功响应:
```json
{ "code": 0, "message": "OK", "data": { "status": "running" } }
```

可能状态:
- pending: 已准备好，等待开始
- running: 正在运行
- finished: 已完成
- failed:dry_run: 预检失败
- error 或 error:<msg>: 运行期错误
- unknown: 未找到状态（例如未曾启动或 Redis 过期）

说明:
- 状态值来源于 Redis 键 {user}_upstream_status。


### 8. 上游处理结果获取

- 接口路径: POST /pipeline/rawdata_results/
- 功能: 上游处理完成后，返回关键结果摘要（当前包括对齐报告与 fastp 报告）
- 权限: 需登录
- 前置条件: 状态为 finished

请求体: 无

未完成时响应:
```json
{ "code": 1, "message": "Upstream analysis not finished yet.", "data": null }
```

完成时成功响应:
```json
{
  "code": 0,
  "message": "Upstream analysis results retrieved successfully.",
  "data": {
    "align_reports": [ { /* 对齐报告记录 */ } ],
    "fastp_reports": [ { /* Fastp 报告记录 */ } ]
  }
}
```

说明:
- 结果存储在 Redis（TTL=600s）。若过期，读取将失败（需重新触发或延长 TTL 配置）。
- 具体字段由后端解析工具输出决定，前端可直接渲染为表格。

### 9. 数据入库提交

- 接口路径: POST /pipeline/put_database/
- 功能: 读取 Redis 中缓存的 sample sheet / gene tpm / gene counts，生成包装数据，分表写入数据库
- 流程:
  1. 读取 3 份 parquet
  2. communicate_id_in_db(): 解析实验类别 & 与数据库实验类别比对 (新增则创建)
  3. db_insert(): 拆分生成 exp_sheet 与 sample_sheet
  4. expression_wrapper(): 生成长表 (TPM / Counts)，附加 UniqueID
  5. 分别调用 put_experiment / put_sample / put_gene_tpm / put_gene_counts
  6. 全部成功返回成功消息
- 前置条件: 前 3 个上传接口均成功且缓存未过期
- 权限: 需登录

请求体: 无

成功响应:
```json
{ "code": 0, "message": "Database data uploaded successfully.", "data": null }
```

部分失败（某一张表写入失败）:
```json
{ "code": 1, "message": "Database data upload failed. Please see log for more information", "data": null }
```

Redis 过期 / 缺失:
```json
{ "code": 1, "message": "Error in putting data into database for user demo: 'NoneType' object has no attribute ...", "data": null }
```

## `validation`验证相关接口

该模块提供访问受保护上传/查询接口所需的认证与用户信息获取。使用 OAuth2 Password (Bearer Token) 模式，客户端先换取 access token，再在后续请求头中携带 Authorization: Bearer <token>。

目前将用户的信息以字典的形式硬编码在`validation.py`的`fake_users_db`中，**在生产环境中应该从数据库中查询用户的信息**。可以在该项目初始化时让用户自定义用户名和密码。

通用说明:
- Token 有效期: 30 分钟
- 口令存储: 后端使用 bcrypt 哈希
- 失败返回: 使用 HTTP 状态码 401 / 400，不走统一 Result 结构
- 成功返回: 标准 JSON，对象字段见下

### 1. 获取访问令牌

- 接口路径: POST /token
- 功能: 通过用户名与密码换取访问令牌 (access_token)
- 权限: 公开
- Content-Type: application/x-www-form-urlencoded

请求体字段 (表单):
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名 (示例: admin) |
| password | string | 是 | 密码 (示例: secret) |

成功响应:
```json
{
  "access_token": "<JWT字符串>",
  "token_type": "bearer"
}
```

失败响应:
- 401 用户名或密码错误
```json
{
  "detail": "Incorrect username or password"
}
```

字段说明:
| 字段 | 说明 |
|------|------|
| access_token | JWT，后续请求认证凭证 |
| token_type | 固定为 bearer |

错误场景:
| 场景 | 触发 | 返回 |
|------|------|------|
| 凭证错误 | 密码或用户名不匹配 | 401 |
| 账号禁用 (预留) | disabled=True | 401 |

### 2. 获取当前用户信息

- 接口路径: GET /admin/user
- 功能: 返回当前已认证用户的基本信息
- 权限: 需登录 (Bearer Token)

请求头:
| 头部 | 示例 |
|------|------|
| Authorization | Bearer <access_token> |


成功响应:
```json
{
  "username": "admin",
  "disabled": false
}
```

失败响应:
- 401 Token 无效 / 过期 / 缺失
```json
{
  "detail": "Could not validate credentials"
}
```
- 400 用户被禁用
```json
{
  "detail": "Inactive user"
}
```

字段说明:
| 字段 | 说明 |
|------|------|
| username | 当前用户名 |
| disabled | 是否禁用 |

处理逻辑摘要:
1. 从 Authorization 头解析 Bearer Token
2. 解码 JWT，校验 exp
3. 载荷中 sub 作为用户名查询内置用户表
4. 校验 disabled 状态
5. 返回用户信息或抛出异常

### 3. 使用 Token 访问受保护接口流程

1. POST /token 获取 access_token
2. 在后续所有需要认证的接口请求头附加:
   Authorization: Bearer <access_token>
3. Token 过期后重新获取

常见错误与排查:
| 现象 | 可能原因 | 处理 |
|------|----------|------|
| 401 Could not validate credentials | Token 缺失/格式错误/过期 | 重新获取 Token |
| 401 Incorrect username or password | 账号或密码错误 | 核对凭证 |
| 400 Inactive user | 用户被禁用 | 启用账号或更换用户 |


