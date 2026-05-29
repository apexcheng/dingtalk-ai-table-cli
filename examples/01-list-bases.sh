#!/bin/bash
# 示例 1：列出所有可访问的 Base

echo "📋 列出所有 Base..."
if [ -n "${DINGTALK_AI_TABLE_DIRECT_URL:-}" ]; then
  mcporter call "$DINGTALK_AI_TABLE_DIRECT_URL" .list_bases limit=10
else
  mcporter call dingtalk-ai-table list_bases limit=10
fi
