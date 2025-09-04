# API接口设计

kafori日本落叶松转录组数据库及分析平台后端API接口设计文档，主要包括以下内容：

1. [analysis_routers.py 分析相关接口](###analysis_routers.py分析相关接口)

## API接口列表

后端API的定义在`backend/routers`文件夹，主要包括以下几个模块：

1. `analysis_routers.py`：与转录组数据分析相关的API接口，用于用户筛选转录组数据后的自定义分析
2. `db_routers.py`：与读取数据库相关的API接口，用于前端页面展示数据库中的数据
3. `file_routers.py`：与用户上传文件相关的API接口，用于用户上传数据到数据库中
4. `routers.py`：与路由相关的API接口，用于处理不同API请求的路由分发
5. `validation.py`：与请求参数验证相关的API接口，用于对部分API接口做验证，仅允许特定用户访问

### analysis_routers分析相关接口



### db_routers数据库相关接口

#### 1. 查询转录组数据库接口

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

### file_routers上传文件接口


本模块用于上传样本信息表与基因表达矩阵，并在全部数据校验通过后一次性写入数据库。Redis 作为临时缓存（每份数据 TTL: 600 秒）。数据提交有两种方式：

1. 样本信息文件 xlsx + 基因表达矩阵 tpm counts（两个csv文件）**已实现**
2. 样本信息文件 xlsx + 原始测序数据 **未实现**

还需要开发：
- 原始测序数据的上传与校验接口
- 原始测序数据的处理与入库逻辑 数据处理需要在后端调用snakemake来运行转录组上游分析的流程，在得到 tpm 和 counts 基因表达矩阵后，可以参照 数据提交方式1 的入库逻辑进行入库

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

#### 1. 上传样本信息表

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

#### 2. 上传基因表达 TPM 矩阵

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

#### 3. 上传基因表达 Counts 矩阵

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

#### 4. 数据入库提交

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

#### 5. 状态与错误总结

| 步骤 | 依赖 | 失败常见原因 | 表现 |
|------|------|--------------|------|
| 上传样本表 | 无 | 文件格式/列缺失 | code=1 |
| 上传TPM | 样本表 | Redis缺失/样本不匹配 | code=1 |
| 上传Counts | 样本表 | 同上 | code=1 |
| 入库 | 三份缓存 | Redis过期/生成包装异常/部分表写入失败 | code=1 |

...existing code...

### validation验证相关接口

该模块提供访问受保护上传/查询接口所需的认证与用户信息获取。使用 OAuth2 Password (Bearer Token) 模式，客户端先换取 access token，再在后续请求头中携带 Authorization: Bearer <token>。

目前将用户的信息以字典的形式硬编码在`validation.py`的`fake_users_db`中，**在生产环境中应该从数据库中查询用户的信息**。可以在该项目初始化时让用户自定义用户名和密码。

通用说明:
- Token 有效期: 30 分钟
- 口令存储: 后端使用 bcrypt 哈希
- 失败返回: 使用 HTTP 状态码 401 / 400，不走统一 Result 结构
- 成功返回: 标准 JSON，对象字段见下

#### 1. 获取访问令牌

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

#### 2. 获取当前用户信息

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

#### 3. 使用 Token 访问受保护接口流程

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


