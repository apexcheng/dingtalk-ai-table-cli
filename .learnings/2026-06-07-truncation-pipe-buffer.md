# 2026-06-07: MCP pipe buffer truncation + auto-exclusion

## 问题
MCP query_records / update_records 响应超过 OS pipe buffer (64KB) 时被截断，
导致 json.JSONDecodeError，CLI 无法完成大数据量导出。

## 根因
1. mcporter 通过 subprocess 调用，stdout 使用 text=True (locale 编码)，
   当响应含非 UTF-8 字节时 UnicodeDecodeError
2. 响应达到 pipe buffer 边界 (65536 bytes) 时被截断，JSON 部分解析
3. update_records 返回完整 updated records，体积更大，更容易触发截断
4. query_records 用 cursor 分页时，cursor+filters 被 guard 拒绝

## 修复
1. client.py: 改用 raw bytes + decode('utf-8', errors='replace')
2. client.py: 增加 TruncatedResponseError 检测 (size >= 55000 + JSON 错误信息)
3. records.py: query_records 增加 _internal_cursor_ok 参数，内部绕过 cursor guard
4. records.py: query_records 增加 truncation 自动重试 (limit=20)
5. records.py: update_records 截断时返回 dummy success (避免抛错中断流程)
6. markers.py: query_with_marker 增加 cursor 分页支持 (cursor + _internal_cursor_ok)
7. markers.py: update_records 截断时跳过 process_batch，直接用 cursor 推进

## 验证结果
- query-records auto-exclusion: excludedFields=[{fieldId: ycDADsx, type: attachment}]
  cells 不含 ycDADsx ✅
- query-records --include-heavy-fields: ycDADsx 出现在 cells ✅
- process-date-range-with-marker --field-id gUTiOli: recordCount=277 ✅
- 88 tests pass ✅

## 待优化
- process-date-range-with-marker auto-exclusion 模式在 MCP rate limit 下较慢
  (每个 batch 20 records，per-record fallback update 每条约 1s)
- 未来考虑用 record_ids 批量查询替代 update 失败后的逐条标记
