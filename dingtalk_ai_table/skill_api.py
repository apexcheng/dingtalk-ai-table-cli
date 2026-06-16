from typing import Any, Callable, Dict, List, Optional

from .attachments import prepare_attachment_upload
from .exports import export_data
from .fields import get_field_id_by_name, get_option_id_by_name, get_table_by_name
from .markers import query_date_range_with_marker, query_with_marker
from .records import create_records, delete_records, query_records, update_records
from .stats import query_records_stats, query_stats

def resolve_field_id(base_id: str, table_id: str, field_name: str) -> str:
    """
    按字段名解析 fieldId。

    :param str base_id: Base ID
    :param str table_id: Table ID
    :param str field_name: 字段名
    :return str: fieldId
    """
    return get_field_id_by_name(base_id, table_id, field_name)


def resolve_option_id(base_id: str, table_id: str, field_name: str, option_name: str) -> str:
    """
    按选项名解析单选/多选的 option id。

    :param str base_id: Base ID
    :param str table_id: Table ID
    :param str field_name: 字段名
    :param str option_name: 选项名
    :return str: option id
    """
    return get_option_id_by_name(base_id, table_id, field_name, option_name)


def resolve_table(base_id: str, table_name: str) -> Dict[str, str]:
    """
    按表名解析 tableId。
    :param str base_id: Base ID
    :param str table_name: 表名
    :return dict: {"tableId": "...", "tableName": "..."}
    """
    return get_table_by_name(base_id, table_name)


def safe_query_records(
    base_id: str,
    table_id: str,
    record_ids: Optional[List[str]] = None,
    filters: Optional[Dict[str, Any]] = None,
    keyword: Optional[str] = None,
    sort: Optional[Any] = None,
    field_ids: Optional[List[str]] = None,
    limit: Optional[int] = None,
    cursor: Optional[str] = None,
) -> Any:
    return query_records(
        base_id=base_id,
        table_id=table_id,
        record_ids=record_ids,
        filters=filters,
        keyword=keyword,
        sort=sort,
        field_ids=field_ids,
        limit=limit,
        cursor=cursor,
    )


def safe_query_stats(
    base_id: str,
    table_id: str,
    stats: Any,
    filters: Optional[Dict[str, Any]] = None,
    group: Optional[str] = None,
    sort_dsl: Optional[str] = None,
    limit: Optional[int] = None,
    data_version: Optional[str] = None,
) -> Any:
    return query_stats(
        base_id=base_id,
        table_id=table_id,
        stats=stats,
        filters=filters,
        group=group,
        sort_dsl=sort_dsl,
        limit=limit,
        data_version=data_version,
    )


def safe_query_records_stats(
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
    return query_records_stats(
        base_id=base_id,
        table_id=table_id,
        stats=stats,
        filters=filters,
        sort=sort,
        keyword=keyword,
        limit=limit,
        data_version=data_version,
        search_field_ids=search_field_ids,
    )


def safe_create_records(base_id: str, table_id: str, records: List[Dict[str, Any]]) -> Any:
    return create_records(base_id, table_id, records)


def safe_update_records(base_id: str, table_id: str, records: List[Dict[str, Any]]) -> Any:
    return update_records(base_id, table_id, records)


def safe_delete_records(base_id: str, table_id: str, record_ids: List[str]) -> Any:
    return delete_records(base_id, table_id, record_ids)


def process_records_with_marker(
    base_id: str,
    table_id: str,
    process_batch: Callable[[List[Dict[str, Any]]], Any],
    filters: Optional[Dict[str, Any]] = None,
    sort: Optional[Any] = None,
    field_ids: Optional[List[str]] = None,
    keyword: Optional[str] = None,
    task_name: str = 'batch_task',
    readonly: bool = False,
) -> str:
    return query_with_marker(
        base_id=base_id,
        table_id=table_id,
        process_batch=process_batch,
        filters=filters,
        sort=sort,
        field_ids=field_ids,
        keyword=keyword,
        task_name=task_name,
        readonly=readonly,
    )


def process_date_range_with_marker(
    base_id: str,
    table_id: str,
    date_field_id: str,
    start_date: str,
    end_date: str,
    process_batch: Callable[[List[Dict[str, Any]]], Any],
    filters: Optional[Dict[str, Any]] = None,
    sort: Optional[Any] = None,
    field_ids: Optional[List[str]] = None,
    keyword: Optional[str] = None,
    task_name: str = 'date_range_task',
    readonly: bool = False,
) -> List[Dict[str, str]]:
    return query_date_range_with_marker(
        base_id=base_id,
        table_id=table_id,
        date_field_id=date_field_id,
        start_date=start_date,
        end_date=end_date,
        process_batch=process_batch,
        filters=filters,
        sort=sort,
        field_ids=field_ids,
        keyword=keyword,
        task_name=task_name,
        readonly=readonly,
    )


def safe_prepare_attachment_upload(
    base_id: str,
    file_name: str,
    size: int,
    mime_type: Optional[str] = None,
) -> Any:
    return prepare_attachment_upload(base_id, file_name, size, mime_type)


def safe_export_data(
    base_id: str,
    scope: Optional[str] = None,
    export_format: Optional[str] = None,
    table_id: Optional[str] = None,
    view_id: Optional[str] = None,
    task_id: Optional[str] = None,
    timeout_ms: Optional[int] = None,
) -> Any:
    return export_data(
        base_id=base_id,
        scope=scope,
        export_format=export_format,
        table_id=table_id,
        view_id=view_id,
        task_id=task_id,
        timeout_ms=timeout_ms,
    )
