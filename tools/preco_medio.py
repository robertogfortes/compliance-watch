"""
Historical average price lookup by service/product category — synthetic data only.
"""
import math

_PRICE_HISTORY: dict[str, list[float]] = {
    "office_equipment": [4200, 4800, 3900, 5100, 4600, 4400, 4750, 4300],
    "office_equipment_maintenance": [4200, 4800, 3900, 5100, 4600, 4400, 4750, 4300],
    "network_infrastructure": [11000, 13500, 12000, 14200, 11800, 12500],
    "consulting": [25000, 30000, 27000, 32000, 28500, 26000, 31000, 29000],
    "software_licensing": [90000, 95000, 88000, 102000, 96000, 91000],
    "facilities": [8000, 8500, 7800, 9000, 8200, 8400],
    "raw_materials": [48000, 51000, 49500, 52000, 50000, 53000, 47500],
    "logistics": [15000, 16500, 14800, 17000, 15500],
}

_SUPPLIER_OVERRIDES: dict[tuple[str, str], list[float]] = {
    ("raw_materials", "SUP-005"): [52000, 51500, 52000, 52500],
}


def _stats(values: list[float]) -> dict:
    n = len(values)
    mean = sum(values) / n
    variance = sum((x - mean) ** 2 for x in values) / n
    std = math.sqrt(variance)
    return {
        "mean": round(mean, 2),
        "std_dev": round(std, 2),
        "min": min(values),
        "max": max(values),
        "sample_count": n,
    }


def _normalize_category(category: str) -> str:
    return category.lower().strip().replace(" ", "_").replace("-", "_")


def consultar_preco_medio(category: str, supplier_id: str | None = None) -> dict:
    """
    Return historical price statistics for a category, optionally filtered to a supplier.

    Raises ValueError for empty category.
    Returns a 'not_found' flag if category is unknown — allows the model to try alternatives.
    """
    if not category or not category.strip():
        raise ValueError("category cannot be empty")

    cat = _normalize_category(category)

    if supplier_id:
        key = (cat, supplier_id.strip())
        if key in _SUPPLIER_OVERRIDES:
            values = _SUPPLIER_OVERRIDES[key]
            return {"category": cat, "supplier_id": supplier_id, "found": True, **_stats(values)}

    if cat in _PRICE_HISTORY:
        values = _PRICE_HISTORY[cat]
        return {"category": cat, "supplier_id": supplier_id, "found": True, **_stats(values)}

    # Partial match
    for known_cat, values in _PRICE_HISTORY.items():
        if cat in known_cat or known_cat in cat:
            return {"category": known_cat, "supplier_id": supplier_id, "found": True, **_stats(values)}

    return {
        "category": category,
        "found": False,
        "known_categories": list(_PRICE_HISTORY.keys()),
        "message": f"No price history for category '{category}'. Try one of the known_categories.",
    }
