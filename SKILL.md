---
name: dingtalk-ai-table
  description: 钉钉 AI 表格（多维表）操作技能。使用 mcporter CLI 连接钉钉官方新版 AI 表格 MCP server，基于 baseId / tableId / fieldId / recordId 体系执行 Base、Table、Field、Record 的查询与增删改。适用于创建 AI 表格、搜索表格、读取表结构、批量增删改记录、批量建字段、更新字段配置、按模板建表等场景。默认使用当前 agent workspace 的 mcporter 注册名 dingtalk-ai-table，`DINGTALK_AI_TABLE_DIRECT_URL` 仅作为可选直连兜底。
version: 0.6.0
metadata:
  author: Marila@Dingtalk
  category: productivity
  tags:
    - dingtalk
    - spreadsheet
    - mcp
    - automation
    - data-management
  documentation: https://github.com/apexcheng/dingtalk-ai-table
  support: https://github.com/apexcheng/dingtalk-ai-table/issues
  openclaw:
    requires:
      bins:
        - mcporter
        - python3
    homepage: https://github.com/apexcheng/dingtalk-ai-table
---

# 钉钉 AI 表格操作（新版 MCP）

## 🚀 5 分钟快速开始

### 1️⃣ 列出我的表格
```bash
mcporter call dingtalk-ai-table list_bases limit=5
```

### 2️⃣ 创建新表格
```bash
mcporter call dingtalk-ai-table create_base baseName='我的项目'
```

### 3️⃣ 添加记录
```bash
mcporter call dingtalk-ai-table create_records \
  --args '{"baseId":"base_xxx","tableId":"tbl_xxx","records":[{"cells":{"fld_name":"张三"}}]}'
```

### 4️⃣ 查询记录
```bash
mcporter call dingtalk-ai-table query_records \
  --args '{"baseId":"base_xxx","tableId":"tbl_xxx","limit":10}'
```

### 5️⃣ 批量导入
```bash
python3 import_records.py base_xxx tbl_xxx data.csv
```

---

## 核心概念

按 **新版 MCP schema** 工作：
- Base：`baseId`
- Table：`tableId`
- Field：`fieldId`
- Record：`recordId`

不要再用旧版 `dentryUuid / sheetIdOrName / fieldIdOrName`。

推荐使用 `mcporter 0.8.1` 及以上版本。

输出模式兼容说明：
- `mcporter 0.8.1+` 可直接调用
- 更低版本需要显式加 `--output text`
- AI 表格 MCP 无论使用哪种模式，返回体本身都是标准 JSON；差异主要在 `mcporter` 的输出处理方式

## 版本守门规则（每个 MCP Server 地址只强制检查一次）

在真正开始任何 AI 表格操作前，必须先检查当前 `mcporter` 注册的 `dingtalk-ai-table` MCP server 实际返回的 tools schema。**但这个检查不该每次都重复做；同一个 MCP Server 地址只需要强制检查一次。**

- 每个 MCP Server 地址首次使用前，先执行一次 `mcporter list dingtalk-ai-table --schema`。
- 同一地址如果已经确认是新版 schema，并且地址没有变化，可以跳过重复检查。
- 如果检查到旧版 schema，先停止使用当前地址，并提示用户更新 MCP Server 配置。
- 详细检查流程、缓存约定和提示文案见 [docs/version-guard.md](docs/version-guard.md)。

## 配置说明

- 默认使用当前 agent workspace 里的 `mcporter` 注册名 `dingtalk-ai-table`。
- 如果需要直连兜底，请使用可选变量 `DINGTALK_AI_TABLE_DIRECT_URL`。
- 安装、注册、`OPENCLAW_WORKSPACE` 和直连示例见 [docs/getting-started.md](docs/getting-started.md)。

## 核心工具集

### 常用数据操作工具
- `get_tables`
- `get_fields`
- `query_records`
- `create_records`
- `update_records`
- `delete_records`
- `prepare_attachment_upload`

### 低频管理工具
- `list_bases`
- `search_bases`
- `get_base`
- `create_base`
- `update_base`
- `delete_base`
- `search_templates`
- `create_table`
- `update_table`
- `delete_table`
- `create_fields`
- `update_field`
- `delete_field`

### 常规流程
1. 先 `get_tables` 看表和字段摘要。
2. 再 `get_fields` 读完整字段配置。
3. 过滤必须用 `fieldId`。
4. 查询用 `query_records`。
5. 新增用 `create_records`。
6. 更新用 `update_records`。
7. 附件先 `prepare_attachment_upload` -> `curl PUT` -> 写 `fileToken`。

详细上手流程见 [docs/getting-started.md](docs/getting-started.md)。

## 查询与写入规则

- `query_records` 不适合做大表全量扫描，不要依赖 `cursor` 连续翻页。
- 不要把“排序 + 过滤 + 翻页”串成连续遍历，也不要单独依赖“排序 + 翻页”或“过滤 + 翻页”做全量处理。
- 批量处理只走“第一页 -> 处理记录 -> 回写辅助标记字段 -> 下次查未标记数据”的方式。
- `filters` 必须使用 `fieldId`；`singleSelect / multipleSelect` 过滤必须传 option id。
- 图片 / 附件字段默认不查；先判断当前 MCP schema 是否支持指定返回字段，支持时就只传非图片 / 非附件 `fieldId`。
- 日期过滤、排序细节和更多示例见 [docs/query-rules.md](docs/query-rules.md)。

## 附件写入

可靠流程：

```bash
mcporter call dingtalk-ai-table prepare_attachment_upload \
  --args '{"baseId":"base_xxx","fileName":"report.pdf","size":102400,"mimeType":"application/pdf"}'

curl -X PUT "<uploadUrl>" \
  -H "Content-Type: application/pdf" \
  --data-binary @report.pdf

mcporter call dingtalk-ai-table create_records \
  --args '{"baseId":"base_xxx","tableId":"tbl_xxx","records":[{"cells":{"fld_attach":[{"fileToken":"ft_xxx"}]}}]}'
```

- `prepare_attachment_upload` 返回 `uploadUrl` 和 `fileToken`，`curl PUT` 后把 `fileToken` 写入记录。
- 其他附件写法和已有附件保留 / 追加规则见 [docs/attachments.md](docs/attachments.md)。

## 脚本

### 批量新增字段

```bash
python3 bulk_add_fields.py <baseId> <tableId> fields.json
```

`fields.json` 示例：

```json
[
  {"fieldName":"任务名","type":"text"},
  {"fieldName":"优先级","type":"singleSelect","config":{"options":[{"name":"高"},{"name":"中"},{"name":"低"}]}}
]
```

兼容项：
- `name` 会自动映射为 `fieldName`
- `phone` 会自动映射为 `telephone`

### 批量导入记录

```bash
python3 import_records.py <baseId> <tableId> data.csv
python3 import_records.py <baseId> <tableId> data.json 50
```

说明：
- CSV 表头默认按 `fieldId` 解释
- JSON 支持：
  - `[{"cells": {...}}]`
  - `[{"fld_xxx": "value"}]`

## 安全规则

- 文件路径受 `OPENCLAW_WORKSPACE` 沙箱限制
- 仅允许读取工作区内 `.json` / `.csv` 文件
- Base / Table / Field / Record ID 都做格式校验
- 批量上限按 MCP server 实际限制控制：
  - `create_fields`：最多 15
  - `get_tables / get_fields`：最多 10
  - `create_records / update_records / delete_records`：最多 100

## 调试原则

- 先 `get_base`，再 `get_tables`，必要时 `get_fields`
- 不要猜 `fieldId`
- 构造过滤条件前，必须先把字段名转换为 fieldId
- 不要依赖“排序 + 过滤 + 翻页”、“排序 + 翻页”、“过滤 + 翻页”做全量遍历
- 批量处理优先使用“查询第一页 + 回写辅助标记字段”的方式推进
- 用户未明确要求图片 / 附件字段时，默认排除图片 / 附件字段
- 复杂参数一律用 `--args` JSON
- `singleSelect / multipleSelect` 过滤时必须传 option ID，不是 option name

## 参考

- API 参考：`references/api-reference.md`
- 错误排查：`references/error-codes.md`
