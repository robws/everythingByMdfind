---
doc_type: reference
date: 2026-05-18
---

# UI Reference

## Running

```
uv run everything.py
```

## Configuration

Config file: `~/.everythingByMdfind.json`

### Exclude patterns

Key: `exclude_patterns` — list of glob patterns; filenames matching any pattern are hidden from results.

Defaults: `~$*`, `*.alias`, `._*`, `.DS_Store`

Example:

```json
{
  "exclude_patterns": ["~$*", "*.alias", "._*", ".DS_Store", "*.tmp"]
}
```
