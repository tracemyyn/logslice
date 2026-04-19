# Field Masking

The `mask` feature partially obscures sensitive field values while preserving
enough context to be useful (e.g. last-four of a card number, domain of an
email address).

## CLI flags

| Flag | Description |
|------|-------------|
| `--mask FIELD:REGEX` | Replace the portion of FIELD matched by REGEX with `*` |
| `--mask-preset FIELD:PRESET` | Apply a named preset to FIELD |
| `--mask-char CHAR` | Use CHAR instead of `*` for masking |

## Presets

| Preset | What it masks |
|--------|---------------|
| `email` | Everything before the `@` sign |
| `card` | All but the last four digits |
| `ip` | First two octets of an IPv4 address |

## Examples

```bash
# Mask email addresses using the built-in preset
logslice --mask-preset user:email app.log

# Mask a bearer token with a custom regex
logslice --mask 'auth:(?<=Bearer )\S+' app.log

# Use a different mask character
logslice --mask-preset card:card --mask-char 'X' payments.log
```

## Python API

```python
from logslice.mask import mask_preset, apply_masks

record = {"email": "alice@example.com", "card": "4111111111111111"}

# Single field
masked = mask_preset(record, "email", "email")
# {'email': '*****@example.com', 'card': '4111111111111111'}

# Batch
results = apply_masks(
    [record],
    [
        {"field": "email", "preset": "email"},
        {"field": "card", "preset": "card"},
    ],
)
```

## Notes

- Masking never mutates the original record dict.
- If the target field is absent the record is returned unchanged.
- Multiple `--mask` / `--mask-preset` flags are applied in order.
