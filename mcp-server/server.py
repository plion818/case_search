import csv
from pathlib import Path

from mcp.server.fastmcp import FastMCP

DATA_FILE = Path(__file__).parent / "case_data.csv"
TAX_RULES_FILE = Path(__file__).parent / "tax_rules.csv"

mcp = FastMCP("case-search-light")


def _normalize_value(value: str) -> int | float | str | None:
    if value is None:
        return None

    value = value.strip()
    if value == "":
        return None

    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def _read_csv_rows(file_path: Path) -> list[dict]:
    try:
        with file_path.open("r", encoding="utf-8-sig", newline="") as file_obj:
            reader = csv.DictReader(file_obj)
            rows: list[dict] = []
            for row in reader:
                normalized = {
                    key: _normalize_value(value) for key, value in row.items()
                }
                rows.append(normalized)
            return rows
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Missing file: {file_path}") from exc


def _load_case_data() -> list[dict]:
    try:
        return _read_csv_rows(DATA_FILE)
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Missing data file: {DATA_FILE}") from exc


def _load_tax_rules() -> list[dict]:
    try:
        return _read_csv_rows(TAX_RULES_FILE)
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Missing tax rules file: {TAX_RULES_FILE}") from exc


def _search_case_by_ban(ban: str) -> dict | None:
    rows = _load_case_data()
    target_ban = ban.upper()

    for row in rows:
        row_ban = row.get("ban")
        if isinstance(row_ban, str) and row_ban.upper() == target_ban:
            return row

    return None


def _get_rules_by_tax_type(tax_type: str) -> list[dict] | None:
    rows = _load_tax_rules()
    filtered_rules = []
    for row in rows:
        if row.get("tax_type") == tax_type:
            filtered_rules.append(row)

    if not filtered_rules:
        return None

    return filtered_rules


@mcp.tool()
def search_case(ban: str) -> dict:
    if not ban:
        raise ValueError("ban is required")

    case_info = _search_case_by_ban(ban)
    if case_info is None:
        raise ValueError(f"No data found for ban: {ban}")

    return case_info


@mcp.tool()
def get_risk_rules(tax_type: str) -> dict:
    if not tax_type:
        raise ValueError("tax_type is required")

    rules = _get_rules_by_tax_type(tax_type)
    if rules is None:
        return {
            "status": "not_available",
            "message": f"No rules found for tax_type: {tax_type}",
            "tax_type": tax_type,
            "rules": [],
        }

    return {
        "status": "success",
        "tax_type": tax_type,
        "rule_count": len(rules),
        "rules": rules,
    }


@mcp.tool()
def math_calculate(operation: str, a: float, b: float) -> dict:
    if operation == "add":
        result = a + b
        symbol = "+"
    elif operation == "subtract":
        result = a - b
        symbol = "-"
    elif operation == "multiply":
        result = a * b
        symbol = "*"
    elif operation == "divide":
        if b == 0:
            raise ValueError("Division by zero is not allowed")
        result = a / b
        symbol = "/"
    else:
        raise ValueError(
            "Unsupported operation. Use one of: add, subtract, multiply, divide"
        )

    return {
        "operation": operation,
        "operands": {"a": a, "b": b},
        "result": result,
        "expression": f"{a} {symbol} {b} = {result}",
    }


if __name__ == "__main__":
    mcp.run()
