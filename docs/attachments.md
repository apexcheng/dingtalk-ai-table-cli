# 附件规则

## 可靠写入流程

`prepare_attachment_upload` -> `curl PUT` -> 写 `fileToken`

```bash
mcporter call dingtalk-ai-table prepare_attachment_upload \
  --args '{"baseId":"base_xxx","fileName":"report.pdf","size":102400,"mimeType":"application/pdf"}'

curl -X PUT "<uploadUrl>" \
  -H "Content-Type: application/pdf" \
  --data-binary @report.pdf

mcporter call dingtalk-ai-table create_records \
  --args '{"baseId":"base_xxx","tableId":"tbl_xxx","records":[{"cells":{"fld_attach":[{"fileToken":"ft_xxx"}]}}]}'
```

## 其他写法

### 直接传外链 URL

```bash
mcporter call dingtalk-ai-table create_records \
  --args '{"baseId":"base_xxx","tableId":"tbl_xxx","records":[{"cells":{"fld_attach":[{"url":"https://example.com/file.pdf"}]}}]}'
```

URL 转存是 best-effort 异步链路，返回成功仅表示已受理，不保证立即可读。可靠写入请用 `fileToken` 方式。

### 原样回传已有附件数据

从 `query_records` 读出的 attachment 单元格数据是完整对象数组，常见形状如下：

```json
[
  {
    "filename": "a.xlsx",
    "size": 92250,
    "type": "xls",
    "resourceId": "<id>",
    "resourceUrl": "<resourceUrl>"
  }
]
```

其中 `type` 是文件类别枚举，常见值为 `"xls"`、`"image"` 等；`resourceUrl` 通常是有时效的下载链接。

如需保留已有附件，把读出的值原样塞回即可。如需追加新附件，把新的 `{"fileToken":"ft_xxx"}` 与已有对象合并成一个数组一起传入。

`update_records` 的 attachment 字段格式相同，传入后会整体覆盖该字段。
