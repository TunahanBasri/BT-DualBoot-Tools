# Reference: Key Formats & Data Schema

This document specifies the exact JSON schema and data normalization rules utilized by `bt-dualboot`.

---

## 1. Export JSON Schema (`btkeys.json`)

```json
[
  {
    "adapter": "4C:03:4F:E0:D1:B0",
    "devices": [
      {
        "mac": "54:46:6B:00:09:FB",
        "name": "Logitech MX Master 3",
        "key": "588546EA82C033CE9508E1C74EC74FD6"
      },
      {
        "mac": "F4:4E:FC:21:44:A8",
        "name": "Keychron K2 Mechanical Keyboard",
        "key": "0123456789ABCDEF0123456789ABCDEF"
      }
    ]
  }
]
```

---

## 2. Field Specifications

| Field | Type | Format | Example | Description |
| :--- | :--- | :--- | :--- | :--- |
| `adapter` | `string` | 12 hex chars (colon/dash/raw) | `4c:03:4f:e0:d1:b0` | Host Bluetooth Controller MAC |
| `devices` | `array` | List of device objects | `[...]` | Paired peripheral list |
| `mac` | `string` | 12 hex chars (colon/dash/raw) | `54:46:6b:00:09:fb` | Peripheral Device MAC |
| `name` | `string` | UTF-8 String | `Logitech MX Master 3` | Friendly Device Name |
| `key` | `string` | 32 hex chars (128-bit) | `588546EA...` | Classic Bluetooth Link Key |

---

## 3. Normalization Rules

- **MAC Address**: Any delimiters (`-`, `:`) are stripped and the string is converted to lowercase with standard colon separation: `xx:xx:xx:xx:xx:xx`.
- **Link Key**: Non-hexadecimal characters (commas, spaces, colons) are stripped and the string is converted to uppercase 32-character hexadecimal.
