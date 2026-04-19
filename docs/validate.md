# Validation

logslice can validate records against rules and either tag or drop invalid entries.

## Rules

Rules are specified with `--validate RULE`. Three forms are supported:

| Form | Meaning |
|------|---------|
| `field` | Field must be present |
| `field:type` | Field must be present and match type (`int`, `float`, `str`, `bool`) |
| `field~pattern` | Field value must match regex pattern |

Multiple `--validate` flags may be combined.

## Options

```
--validate RULE      Add a validation rule (repeatable)
--drop-invalid       Drop records that fail any rule
--tag-errors FIELD   Attach list of error messages to FIELD on each record
```

## Examples

Drop records missing `level`:

```bash
logslice app.log --validate level --drop-invalid
```

Ensure `status` is an integer:

```bash
logslice app.log --validate status:int --drop-invalid
```

Tag errors onto records without removing them:

```bash
logslice app.log --validate level --tag-errors _errors
```

Combine rules:

```bash
logslice app.log --validate level --validate status:int --validate msg~'\S+' --drop-invalid
```

## Programmatic use

```python
from logslice.validate import validate_record, apply_validation, parse_rule_arg

rules = [parse_rule_arg("level"), parse_rule_arg("status:int")]
errors = validate_record(record, rules)
clean, n_invalid = apply_validation(records, rules, drop_invalid=True)
```
