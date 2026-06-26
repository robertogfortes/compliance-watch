"""
Supplier registry lookup — synthetic data only.

All supplier records are fictional. No real company names, tax IDs, or individuals.
"""

_SUPPLIER_REGISTRY: dict[str, dict] = {
    "SUP-001": {
        "name": "Synthex Supplies Ltda",
        "registry_id": "SUP-001",
        "status": "active",
        "category": "office_equipment",
        "registered_since": "2019-03-01",
        "compliance_notes": None,
    },
    "SUP-002": {
        "name": "Nexoria Consulting S.A.",
        "registry_id": "SUP-002",
        "status": "active",
        "category": "consulting",
        "registered_since": "2020-07-15",
        "compliance_notes": None,
    },
    "SUP-003": {
        "name": "Veltron Technology Partners",
        "registry_id": "SUP-003",
        "status": "active",
        "category": "software_licensing",
        "registered_since": "2018-11-20",
        "compliance_notes": "Annual renewal pending review",
    },
    "SUP-004": {
        "name": "Auramid Facilities Ltda",
        "registry_id": "SUP-004",
        "status": "active",
        "category": "facilities",
        "registered_since": "2021-01-10",
        "compliance_notes": None,
    },
    "SUP-005": {
        "name": "Cortex Supply Chain Ltda",
        "registry_id": "SUP-005",
        "status": "suspended",
        "category": "raw_materials",
        "registered_since": "2017-06-05",
        "compliance_notes": "Suspended 2024-02-28: duplicate billing investigation ongoing",
    },
    "SUP-006": {
        "name": "Helix Logistics Group",
        "registry_id": "SUP-006",
        "status": "active",
        "category": "logistics",
        "registered_since": "2022-04-18",
        "compliance_notes": None,
    },
}

_NAME_INDEX = {v["name"].lower(): k for k, v in _SUPPLIER_REGISTRY.items()}


def consultar_fornecedor(supplier_id: str) -> dict:
    """
    Look up a supplier by name or registry ID.

    Raises ValueError with a descriptive message if not found,
    so the model can self-correct with a better query.
    """
    if not supplier_id or not supplier_id.strip():
        raise ValueError("supplier_id cannot be empty")

    key = supplier_id.strip()

    if key in _SUPPLIER_REGISTRY:
        return _SUPPLIER_REGISTRY[key]

    lower = key.lower()
    if lower in _NAME_INDEX:
        return _SUPPLIER_REGISTRY[_NAME_INDEX[lower]]

    # Partial name match
    for name_lower, reg_id in _NAME_INDEX.items():
        if lower in name_lower or name_lower in lower:
            return _SUPPLIER_REGISTRY[reg_id]

    raise ValueError(
        f"Supplier not found: '{supplier_id}'. "
        f"Known IDs: {list(_SUPPLIER_REGISTRY.keys())}. "
        "Try using the full supplier name or the SUP-NNN registry ID."
    )
