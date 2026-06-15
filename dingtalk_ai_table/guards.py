import re
from datetime import datetime
from typing import Any, Optional

MAX_QUERY_LIMIT = 100
DEFAULT_QUERY_LIMIT = 100
MAX_RECORDS_PER_BATCH = 100
MAX_FIELDS_PER_CREATE = 15
MAX_TABLES_PER_GET = 10
MAX_FIELDS_PER_GET = 10
QUERY_MARK_FIELD_NAME = "查询标记"
SUPPORTED_FILTER_OPERATORS = {
    "eq",
    "ne",
    "exist",
    "un_exist",
    "lt",
    "gt",
    "lte",
    "gte",
    "contain",
    "exclusive",
    "all_of",
    "any_of",
    "none_of",
    "date_eq",
    "before",
    "after",
    "not_before",
    "not_after",
    "from_now",
    "date_between",
}
RESOURCE_ID_PATTERN = r"^[A-Za-z0-9_-]{4,128}$"

COMPOUND_FILTER_OPERATORS = {"and", "or"}
EXISTENCE_FILTER_OPERATORS = {"exist", "un_exist"}
DATE_VALUE_FILTER_OPERATORS = {"date_eq", "before", "after", "not_before", "not_after"}
DATE_RANGE_FILTER_OPERATORS = {"date_between"}
FORBIDDEN_FILTER_OPERATORS = {"greater_equal", "less_than", "is_after", "is_before"}
FORBIDDEN_QUERY_MARK_FIELD_NAMES = {
    "处理标记",
    "同步标记",
    "回查标记",
    "AI处理标记",
}

_RESOURCE_ID_RE = re.compile(RESOURCE_ID_PATTERN)
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def validate_resource_id(value: Any) -> bool:
    return bool(isinstance(value, str) and value.strip() and _RESOURCE_ID_RE.match(value.strip()))


def validate_dentry_uuid(value: Any) -> bool:
    return validate_resource_id(value)


def ensure_resource_id(value: Any, field_name: str) -> str:
    if not validate_resource_id(value):
        raise ValueError(f"错误：无效的 {field_name} 格式")
    return value.strip()


def normalize_query_limit(limit: Optional[int]) -> int:
    if limit is None:
        return DEFAULT_QUERY_LIMIT

    if not isinstance(limit, int):
        raise ValueError("limit 必须是整数")
    if limit <= 0:
        raise ValueError("limit 必须大于 0")
    if limit > MAX_QUERY_LIMIT:
        raise ValueError(f"query_records 单次 limit 最大只能是 {MAX_QUERY_LIMIT}")
    return limit


def validate_record_batch(records: Any) -> Any:
    if not isinstance(records, list):
        raise ValueError("records 必须是数组")
    if not records:
        raise ValueError("批量参数必须是非空数组")
    if len(records) > MAX_RECORDS_PER_BATCH:
        raise ValueError(f"单次最多 {MAX_RECORDS_PER_BATCH} 条记录")
    return records


def validate_field_batch(fields: Any) -> Any:
    if not isinstance(fields, list):
        raise ValueError("fields 必须是数组")
    if not fields:
        raise ValueError("批量参数必须是非空数组")
    if len(fields) > MAX_FIELDS_PER_CREATE:
        raise ValueError(f"单次最多创建 {MAX_FIELDS_PER_CREATE} 个字段，请拆分后重试")
    return fields


def validate_get_tables_batch(table_ids: Any) -> Any:
    if not isinstance(table_ids, list):
        raise ValueError("tableIds 必须是数组")
    if not table_ids:
        raise ValueError("批量参数必须是非空数组")
    if len(table_ids) > MAX_TABLES_PER_GET:
        raise ValueError(f"get_tables 单次最多 {MAX_TABLES_PER_GET} 个 tableId")
    return table_ids


def validate_get_fields_batch(field_ids: Any) -> Any:
    if not isinstance(field_ids, list):
        raise ValueError("fieldIds 必须是数组")
    if not field_ids:
        raise ValueError("批量参数必须是非空数组")
    if len(field_ids) > MAX_FIELDS_PER_GET:
        raise ValueError(f"get_fields 单次最多 {MAX_FIELDS_PER_GET} 个 fieldId")
    return field_ids


def validate_no_cursor_with_sort(sort: Any, cursor: Any) -> None:
    if cursor not in (None, "") and sort is not None:
        raise ValueError("sort 场景下禁止传 cursor，必须改用查询标记推进")


# Backward-compatible alias for older call sites.
# filters + cursor is now allowed; only sort + cursor is rejected.
def validate_no_cursor_with_filters_or_sort(filters: Any, sort: Any, cursor: Any) -> None:
    del filters
    return validate_no_cursor_with_sort(sort, cursor)


def validate_date_string(value: Any) -> str:
    if not isinstance(value, str) or not _DATE_RE.match(value):
        raise ValueError("日期过滤值只允许 YYYY-MM-DD")

    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        raise ValueError("日期过滤值只允许 YYYY-MM-DD")
    return value


def validate_query_mark_field_name(field_name: Any) -> str:
    if field_name == QUERY_MARK_FIELD_NAME:
        return field_name
    if field_name in FORBIDDEN_QUERY_MARK_FIELD_NAMES:
        raise ValueError(f"查询标记字段名只能使用 {QUERY_MARK_FIELD_NAME}，禁止使用 {field_name}")
    raise ValueError(f"查询标记字段名只能使用 {QUERY_MARK_FIELD_NAME}")


def _validate_filter_operands(operator: str, operands: Any) -> None:
    if not isinstance(operands, list):
        raise ValueError("filters.operands 必须是数组")

    if operator in COMPOUND_FILTER_OPERATORS:
        if not operands:
            raise ValueError(f"{operator} 过滤条件不能为空")
        for operand in operands:
            validate_filter_tree(operand)
        return

    if operator in EXISTENCE_FILTER_OPERATORS:
        if len(operands) != 1:
            raise ValueError(f"{operator} 过滤条件必须包含 [fieldId]")
        ensure_resource_id(operands[0], "fieldId")
        return

    if len(operands) != 2:
        raise ValueError(f"{operator} 过滤条件必须包含 [fieldId, value]")

    field_id = ensure_resource_id(operands[0], "fieldId")
    value = operands[1]
    if operator in DATE_VALUE_FILTER_OPERATORS:
        validate_date_string(value)
    elif operator in DATE_RANGE_FILTER_OPERATORS:
        if not isinstance(value, list) or len(value) != 2:
            raise ValueError(f"{operator} 过滤值必须是 [start, end]")
        validate_date_string(value[0])
        validate_date_string(value[1])
    elif field_id and value is None:
        raise ValueError(f"{operator} 过滤值不能为 null")


def validate_filter_tree(filters: Any) -> Any:
    if filters is None:
        return None

    if not isinstance(filters, dict):
        raise ValueError("filters 必须是对象")

    if "filterType" in filters:
        raise ValueError("filterType is not supported")
    if "fieldName" in filters:
        raise ValueError("fieldName is not supported")

    operator = filters.get("operator")
    if operator not in SUPPORTED_FILTER_OPERATORS and operator not in COMPOUND_FILTER_OPERATORS:
        if operator in FORBIDDEN_FILTER_OPERATORS:
            raise ValueError(f"当前不支持 {operator} 过滤器")
        raise ValueError(f"不支持的过滤器操作符: {operator}")

    operands = filters.get("operands")
    _validate_filter_operands(operator, operands)
    return filters
