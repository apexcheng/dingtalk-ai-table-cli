---
name: dingtalk-ai-table
description: OpenClaw 调用钉钉 AI 表格 MCP 的安全调用层。Agent 不直接手拼 mcporter 参数，而是优先调用 dingtalk_ai_table 包导出的 Python 函数，由 Python 层完成参数校验、分页限制、字段 ID 校验、查询标记分页和附件上传前置。
version: 0.7.3
metadata:
  author: Marila@Dingtalk
  category: productivity
  tags:
    - dingtalk
    - spreadsheet
    - mcp
    - automation
    - data-management
  documentation: https://github.com/apexcheng/dingtalk-ai-tableV2
  support: https://github.com/apexcheng/dingtalk-ai-tableV2/issues
  openclaw:
    requires:
      bins:
        - mcporter
        - python3
    homepage: https://github.com/apexcheng/dingtalk-ai-tableV2
---

# dingtalk-ai-table OpenClaw Skill

这是钉钉 AI 表格 MCP 的 **Python 安全调用层**。

它不是钉钉 AI 表格服务端，不是完整 SDK，也不是通用 CLI 工具。

它的作用是：让 OpenClaw / Agent 通过少量 Python 函数安全地查询、创建、更新、删除钉钉 AI 表格记录，并把容易出错的 MCP 调用规则硬写进 Python 代码里。

## 什么时候使用

当用户要求操作钉钉 AI 表格、多维表、Base、Table、Field、Record 时，使用本 skill。

典型任务：

- 查询表格记录
- 新增记录
- 更新记录
- 删除记录
- 根据字段名查 fieldId
- 根据单选 / 多选名称查 option id
- 带过滤条件批量处理记录
- 日期范围批量处理记录
- 上传附件前获取上传信息

## 什么时候不要使用

不要把本 skill 当成完整 SDK 使用。

不要用它做：

- 通用数据导入工具
- 任意文件处理工具
- 非钉钉 AI 表格任务
- 绕过 MCP 服务端限制
- 让 Agent 自己拼复杂 mcporter 参数

## 唯一推荐入口

OpenClaw / Agent 优先只调用包根导出的这些函数：

```python
from dingtalk_ai_table import (
    resolve_field_id,
    resolve_option_id,
    safe_query_records,
    safe_create_records,
    safe_update_records,
    safe_delete_records,
    process_records_with_marker,
    process_date_range_with_marker,
    safe_prepare_attachment_upload,
)
```

## 基本调用流程

1. 如果只有字段名，先用 `resolve_field_id` 查 `fieldId`
2. 如果是单选 / 多选过滤，先用 `resolve_option_id` 查 option id
3. 普通查询用 `safe_query_records`
4. 新增记录用 `safe_create_records`
5. 更新记录用 `safe_update_records`
6. 删除记录用 `safe_delete_records`
7. 带 `filters` 或 `sort` 且可能超过 100 条时，用 `process_records_with_marker`
8. 日期范围查询用 `process_date_range_with_marker`
9. 附件上传前先用 `safe_prepare_attachment_upload`

## 硬限制

必须遵守：

- `query_records.limit` 最大只能是 `100`
- `query_records` 不传 `limit` 时默认按 `100` 处理
- 只要出现 `filters` 或 `sort`，就禁止传 `cursor`
- `filters` 必须是对象结构，不能是数组
- 禁止使用 `filterType`
- 过滤字段必须使用 `fieldId`，不能使用字段名
- 写入 `cells` 时，key 必须是 `fieldId`
- 只允许过滤 operator：`eq`、`ne`、`date_eq`
- 禁止使用：`gte`、`lte`、`greater_equal`、`less_than`、`is_after`、`is_before`
- `date_eq` 只接受 `YYYY-MM-DD`
- 单选 / 多选过滤必须使用 option id
- `create_fields` 单次最多 `15` 个字段
- `get_tables` / `get_fields` 单次最多 `10` 个对象
- `create_records` / `update_records` / `delete_records` 单次最多 `100` 条
- `查询标记` 是唯一允许的辅助分页字段名
- 附件可靠写入必须先 `prepare_attachment_upload`

## 禁止行为

Agent 不要做这些事：

- 不要直接猜 `fieldId`
- 不要直接猜 option id
- 不要用字段名写入 `cells`
- 不要手拼复杂 `filters`
- 不要在有 `filters` 或 `sort` 时继续用 `cursor`
- 不要默认全量查询后本地筛选
- 不要生成日期区间过滤条件
- 不要用 `gte / lte` 查询日期范围
- 不要把图片 / 附件字段默认查出来
- 不要绕过 Python 安全函数直接拼 MCP 参数

## mcporter 说明

本项目内部通过 `mcporter call dingtalk-ai-table ...` 调用 MCP。

Agent 正常情况下不需要手写 `mcporter call`。
只有在调试 MCP 注册状态时，才检查：

```bash
mcporter list dingtalk-ai-table --schema
```

如果当前环境没有注册名，可用环境变量兜底：

```bash
export DINGTALK_AI_TABLE_DIRECT_URL="你的 MCP Server URL"
```

但业务调用仍然优先走 Python 安全函数。

## 最小示例

```python
from dingtalk_ai_table import resolve_field_id, safe_query_records
from dingtalk_ai_table.filters import eq_filter

status_field_id = resolve_field_id(
    base_id="base_xxxxxxxx",
    table_id="tbl_xxxxxxxx",
    field_name="状态",
)

filters = eq_filter(status_field_id, "待处理")

result = safe_query_records(
    base_id="base_xxxxxxxx",
    table_id="tbl_xxxxxxxx",
    filters=filters,
    limit=100,
)

print(result)
```

## 总原则

优先让 Python 层拦截错误参数。
不要只依赖提示词约束 Agent 行为。
除非真实调用中发现 MCP 返回结构变化，否则不要扩大功能范围。
