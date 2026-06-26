"""
Blocked-supplier list lookup — synthetic data only.
"""
import datetime

_BLOCKED_LIST: dict[str, dict] = {
    "SUP-005": {
        "supplier_id": "SUP-005",
        "supplier_name": "Cortex Supply Chain Ltda",
        "blocked": True,
        "reason": "Duplicate billing investigation: invoices INV-CRT-2024-055 and INV-CRT-2024-088 submitted for identical batch",
        "date_added": "2024-02-28",
        "added_by": "compliance_team",
    },
    "SUP-007": {
        "supplier_id": "SUP-007",
        "supplier_name": "Orbita Services ME",
        "blocked": True,
        "reason": "Contract signed without mandatory second quotation (policy violation ref. POL-PROC-003)",
        "date_added": "2023-11-14",
        "added_by": "internal_audit",
    },
}

_NAME_INDEX = {v["supplier_name"].lower(): k for k, v in _BLOCKED_LIST.items()}


def consultar_lista_bloqueio(supplier_id: str) -> dict:
    """
    Check whether a supplier is on the blocked list.

    Always returns a result dict — blocked=False if not found on the list.
    Raises ValueError only on empty input.
    """
    if not supplier_id or not supplier_id.strip():
        raise ValueError("supplier_id cannot be empty")

    key = supplier_id.strip()

    if key in _BLOCKED_LIST:
        return _BLOCKED_LIST[key]

    lower = key.lower()
    if lower in _NAME_INDEX:
        return _BLOCKED_LIST[_NAME_INDEX[lower]]

    for name_lower, reg_id in _NAME_INDEX.items():
        if lower in name_lower or name_lower in lower:
            return _BLOCKED_LIST[reg_id]

    return {
        "supplier_id": supplier_id,
        "blocked": False,
        "reason": None,
        "date_added": None,
        "checked_at": datetime.date.today().isoformat(),
    }
