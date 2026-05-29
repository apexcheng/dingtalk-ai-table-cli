# 版本守门规则

## 目标

每个 MCP Server 地址只做一次强制 schema 检查，避免重复探测。

## 一次性检查策略

1. 先读取当前 `mcporter` 里 `dingtalk-ai-table` 对应的 MCP Server 地址。
2. 用这个地址生成一个本地检查标记，建议基于完整 URL 或其 hash。
3. 将检查结果缓存到工作区，例如：

```text
~/.openclaw/workspace/.cache/dingtalk-ai-table/
```

建议文件名模式：

```text
schema-check-<url-hash>.json
```

4. 如果当前地址对应的检查标记已经存在，并且结果是“已确认新版 schema”，则跳过重复检查。
5. 只有在以下情况才重新强制检查：
   - 第一次运行，没有检查标记
   - `mcporter` 里的 MCP Server 地址变了
   - 之前检查结果是旧版 schema / 检查失败
   - 用户明确要求重新验证

## 强制检查命令

```bash
mcporter list dingtalk-ai-table --schema
```

## 判定标准

如果返回的 tools 仍然是旧版这一套，例如：

- `get_root_node_of_my_document`
- `create_base_app`
- `list_base_tables`
- `add_base_record`
- `search_base_record`
- `list_base_field`

或者整体仍然基于：

- `dentryUuid`
- `sheetIdOrName`
- `fieldIdOrName`

就说明当前注册的 MCP Server 还是旧地址，不能继续操作。

新版 schema 应该出现的 tools 示例：

- `list_bases`
- `get_base`
- `get_tables`
- `get_fields`
- `query_records`
- `create_records`
- `update_records`
- `delete_records`
- `prepare_attachment_upload`

## 发现旧版时怎么处理

1. 打开这个页面：
   `https://mcp.dingtalk.com/#/detail?mcpId=9555&detailType=marketMcpDetail`
2. 点击右侧“获取 MCP Server 配置”按钮
3. 复制新的 MCP Server 地址
4. 用新的地址替换 `mcporter` 里已注册的 `dingtalk-ai-table`
5. 替换后重新执行：

```bash
mcporter list dingtalk-ai-table --schema
```

## 可复用提示文案

```text
当前 mcporter 里注册的 dingtalk-ai-table 还是旧版 MCP schema，暂时不能按新版技能操作。
请打开 https://mcp.dingtalk.com/#/detail?mcpId=9555&detailType=marketMcpDetail ，点击右侧“获取 MCP Server 配置”按钮，复制新的 MCP Server 地址，并替换 mcporter 里已注册的 dingtalk-ai-table 地址。替换后重新检查 schema，确认出现 list_bases / get_base / create_records 等新版 tools 后，再继续操作 AI 表格。
```
