import json
from typing import Any, Dict, Optional

from .client import run_mcporter
from .guards import ensure_resource_id

EXPORT_SCOPES = {"all", "table", "view"}
EXPORT_FORMATS = {"excel", "attachment", "excel_and_attachment", "excel_with_inline_images"}


def export_data(
    base_id: str,
    scope: Optional[str] = None,
    export_format: Optional[str] = None,
    table_id: Optional[str] = None,
    view_id: Optional[str] = None,
    task_id: Optional[str] = None,
    timeout_ms: Optional[int] = None,
) -> Any:
    base_id = ensure_resource_id(base_id, "baseId")
    payload: Dict[str, Any] = {
        "baseId": base_id,
    }

    if task_id:
        if not isinstance(task_id, str) or not task_id.strip():
            raise ValueError("taskId 不能为空")
        payload["taskId"] = task_id.strip()
    else:
        if scope not in EXPORT_SCOPES:
            raise ValueError("scope 必须是 all/table/view 之一")
        if export_format not in EXPORT_FORMATS:
            raise ValueError("format 必须是 excel/attachment/excel_and_attachment/excel_with_inline_images 之一")
        payload["scope"] = scope
        payload["format"] = export_format
        if scope in {"table", "view"}:
            payload["tableId"] = ensure_resource_id(table_id, "tableId")
        elif table_id:
            payload["tableId"] = ensure_resource_id(table_id, "tableId")
        if scope == "view":
            payload["viewId"] = ensure_resource_id(view_id, "viewId")
        elif view_id:
            payload["viewId"] = ensure_resource_id(view_id, "viewId")

    if timeout_ms is not None:
        payload["timeoutMs"] = timeout_ms
    return run_mcporter(["export_data", "--args", json.dumps(payload, ensure_ascii=False)], timeout=120)
