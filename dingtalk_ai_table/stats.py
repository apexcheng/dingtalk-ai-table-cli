import json
from typing import Any, Dict, Optional

from .client import run_mcporter
from .guards import ensure_resource_id, validate_filter_tree


def _validate_stats(stats: Any) -> Any:
    if not isinstance(stats, list):
        raise ValueError("stats 必须是数组")
    if not stats:
        raise ValueError("stats 不能为空")
    if len(stats) > 20:
        raise ValueError("stats 单次最多 20 项")
    for index, item in enumerate(stats):
        if not isinstance(item, dict):
            raise ValueError(f"stats #{index + 1} 必须是对象")
        ensure_resource_id(item.get("fieldId"), "fieldId")
        stats_type = item.get("statsType")
        if not isinstance(stats_type, str) or not stats_type.strip():
            raise ValueError(f"stats #{index + 1} 缺少 statsType")
    return stats


def query_stats(
    base_id: str,
    table_id: str,
    stats: Any,
    filters: Optional[Dict[str, Any]] = None,
    group: Optional[str] = None,
    sort_dsl: Optional[str] = None,
    limit: Optional[int] = None,
    data_version: Optional[str] = None,
) -> Any:
    base_id = ensure_resource_id(base_id, "baseId")
    table_id = ensure_resource_id(table_id, "tableId")
    _validate_stats(stats)
    validate_filter_tree(filters)

    payload: Dict[str, Any] = {
        "baseId": base_id,
        "tableId": table_id,
        "stats": stats,
    }
    if filters is not None:
        payload["filters"] = filters
    if group is not None:
        payload["group"] = group
    if sort_dsl is not None:
        payload["sortDsl"] = sort_dsl
    if limit is not None:
        payload["limit"] = limit
    if data_version is not None:
        payload["dataVersion"] = data_version
    return run_mcporter(["query_stats", "--args", json.dumps(payload, ensure_ascii=False)])


def query_records_stats(
    base_id: str,
    table_id: str,
    stats: Any,
    filters: Optional[Dict[str, Any]] = None,
    sort: Optional[str] = None,
    keyword: Optional[str] = None,
    limit: Optional[int] = None,
    data_version: Optional[str] = None,
    search_field_ids: Optional[Any] = None,
) -> Any:
    base_id = ensure_resource_id(base_id, "baseId")
    table_id = ensure_resource_id(table_id, "tableId")
    _validate_stats(stats)
    validate_filter_tree(filters)

    payload: Dict[str, Any] = {
        "baseId": base_id,
        "tableId": table_id,
        "stats": stats,
    }
    if filters is not None:
        payload["filters"] = filters
    if sort is not None:
        payload["sort"] = sort
    if keyword is not None:
        payload["keyword"] = keyword
    if limit is not None:
        payload["limit"] = limit
    if data_version is not None:
        payload["dataVersion"] = data_version
    if search_field_ids is not None:
        if not isinstance(search_field_ids, list):
            raise ValueError("searchFieldIds 必须是数组")
        payload["searchFieldIds"] = [
            ensure_resource_id(field_id, "fieldId") for field_id in search_field_ids
        ]
    return run_mcporter(["query_records_stats", "--args", json.dumps(payload, ensure_ascii=False)])
