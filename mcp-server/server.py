from pathlib import Path

import pandas as pd
from mcp.server.fastmcp import FastMCP

DATA_FILE = Path(__file__).parent / "case_data.csv"
TAX_RULES_FILE = Path(__file__).parent / "tax_rules.csv"

mcp = FastMCP("case-search-light")


def _load_case_data() -> pd.DataFrame:
    try:
        return pd.read_csv(DATA_FILE)
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Missing data file: {DATA_FILE}") from exc


def _load_tax_rules() -> pd.DataFrame:
    try:
        return pd.read_csv(TAX_RULES_FILE)
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Missing tax rules file: {TAX_RULES_FILE}") from exc


def _search_case_by_ban(ban: str) -> dict | None:
    df = _load_case_data()
    result = df[df["ban"].str.upper() == ban.upper()]

    if result.empty:
        return None

    case_info = result.iloc[0].to_dict()
    for key, value in case_info.items():
        if pd.isna(value):
            case_info[key] = None

    return case_info


def _get_rules_by_tax_type(tax_type: str) -> list[dict] | None:
    df = _load_tax_rules()
    filtered_rules = df[df["tax_type"] == tax_type]

    if filtered_rules.empty:
        return None

    rules_list = filtered_rules.to_dict("records")
    for rule in rules_list:
        for key, value in rule.items():
            if pd.isna(value):
                rule[key] = None

    return rules_list


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
