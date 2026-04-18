# Pivot

The `pivot` module transposes structured log records so that distinct values
of one field become columns, enabling side-by-side comparison of metrics.

## Functions

### `pivot_records(records, index_field, column_field, value_field)`

Groups records by `index_field`. For each group the value of `column_field`
becomes a new key whose value is taken from `value_field`.

```python
from logslice.pivot import pivot_records

records = [
    {"host": "web-1", "metric": "cpu", "value": 55},
    {"host": "web-1", "metric": "mem", "value": 70},
    {"host": "web-2", "metric": "cpu", "value": 30},
]

result = pivot_records(records, "host", "metric", "value")
# [{"host": "web-1", "cpu": 55, "mem": 70},
#  {"host": "web-2", "cpu": 30}]
```

### `column_names(pivoted, index_field)`

Returns a sorted list of all column names present in the pivoted output,
excluding the index field itself. Useful for rendering tables.

### `fill_missing(pivoted, columns, fill_value=None)`

Ensures every row contains every column. Missing entries are filled with
`fill_value` (default `None`). The original records are not mutated.

## Typical workflow

```python
from logslice.pivot import pivot_records, column_names, fill_missing

pivoted = pivot_records(records, "host", "metric", "value")
cols = column_names(pivoted, "host")
full = fill_missing(pivoted, cols, fill_value=0)
```
