# case_search_light

A lightweight FastMCP server based on case_search.

## Included tools

- `search_case`
- `get_risk_rules`
- `math_calculate`

No environment variables are required.

## Run

```bash
pip install -r requirements.txt
python mcp-server/server.py
```

## Example platform start command

```bash
sh -c "pip install --quiet -r requirements.txt && exec python mcp-server/server.py"
```
