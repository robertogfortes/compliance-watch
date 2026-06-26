"""
Generate synthetic PDF fixtures for extraction tests.

All names, numbers, and values are fictional. Run once and commit the PDFs.
Requires: pip install reportlab
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "tests", "fixtures")

SYNTHETIC_DOCUMENTS = [
    {
        "filename": "invoice_synthex_001.pdf",
        "content": [
            ("INVOICE", 24, True),
            ("Document No: INV-SYN-2024-001", 12, False),
            ("Supplier: Synthex Supplies Ltda", 12, False),
            ("Issue Date: 2024-03-15", 12, False),
            ("", 12, False),
            ("Items:", 12, True),
            ("  - Office equipment maintenance   BRL 4,500.00", 12, False),
            ("  - Network infrastructure upgrade  BRL 12,800.00", 12, False),
            ("", 12, False),
            ("Total: BRL 17,300.00", 14, True),
        ],
    },
    {
        "filename": "invoice_nexoria_002.pdf",
        "content": [
            ("NOTA FISCAL DE SERVICO", 20, True),
            ("Numero: NF-NEX-2024-0042", 12, False),
            ("Prestador: Nexoria Consulting S.A.", 12, False),
            ("Data de Emissao: 2024-04-02", 12, False),
            ("", 12, False),
            ("Descricao dos Servicos:", 12, True),
            ("  - Consultoria em compliance regulatorio   BRL 28,000.00", 12, False),
            ("  - Revisao de contratos (20 horas)         BRL 6,000.00", 12, False),
            ("", 12, False),
            ("Valor Total: BRL 34,000.00", 14, True),
        ],
    },
    {
        "filename": "contract_veltron_003.pdf",
        "content": [
            ("SERVICE CONTRACT", 20, True),
            ("Contract No: CTR-VLT-2024-007", 12, False),
            ("Counterpart: Veltron Technology Partners", 12, False),
            ("Effective Date: 2024-01-10", 12, False),
            ("Expiry Date: 2024-12-31", 12, False),
            ("", 12, False),
            ("Scope of Services:", 12, True),
            ("  Annual software licensing and support for internal ERP modules.", 12, False),
            ("", 12, False),
            ("Contract Value: BRL 96,000.00 (annual)", 14, True),
            ("Payment: 12 monthly instalments of BRL 8,000.00", 12, False),
            ("", 12, False),
            ("Second quotation obtained: YES (Ref: QUOT-VLT-2023-19, QUOT-AUR-2023-22)", 12, False),
        ],
    },
    {
        "filename": "addendum_auramid_004.pdf",
        "content": [
            ("CONTRACT ADDENDUM", 20, True),
            ("Addendum No: ADD-AUR-2024-002", 12, False),
            ("Original Contract: CTR-AUR-2023-015", 12, False),
            ("Supplier: Auramid Facilities Ltda", 12, False),
            ("Addendum Date: 2024-05-20", 12, False),
            ("", 12, False),
            ("Reason for Addendum:", 12, True),
            ("  Extension of cleaning services scope to include Building C.", 12, False),
            ("", 12, False),
            ("Value Adjustment: + BRL 3,200.00 / month", 14, True),
            ("New Monthly Total: BRL 11,700.00", 12, False),
        ],
    },
    {
        "filename": "invoice_cortex_005.pdf",
        "content": [
            ("INVOICE — DUPLICATE RISK TEST", 20, True),
            ("Document No: INV-CRT-2024-088", 12, False),
            ("Supplier: Cortex Supply Chain Ltda", 12, False),
            ("Issue Date: 2024-06-01", 12, False),
            ("", 12, False),
            ("Note: This document has the same supplier and value as INV-CRT-2024-055", 11, False),
            ("submitted on 2024-05-15. Flagged for duplicate payment review.", 11, False),
            ("", 12, False),
            ("Items:", 12, True),
            ("  - Raw material batch #RM-2024-C88   BRL 52,000.00", 12, False),
            ("", 12, False),
            ("Total: BRL 52,000.00", 14, True),
        ],
    },
]


def generate_pdfs():
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
    except ImportError:
        print("reportlab not installed. Run: pip install reportlab")
        sys.exit(1)

    os.makedirs(FIXTURES_DIR, exist_ok=True)

    for doc in SYNTHETIC_DOCUMENTS:
        path = os.path.join(FIXTURES_DIR, doc["filename"])
        c = canvas.Canvas(path, pagesize=A4)
        _, height = A4
        y = height - 60

        for text, size, bold in doc["content"]:
            c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
            c.drawString(60, y, text)
            y -= size + 8
            if y < 80:
                c.showPage()
                y = height - 60

        c.save()
        print(f"Generated: {path}")

    print(f"\n{len(SYNTHETIC_DOCUMENTS)} fixtures written to {FIXTURES_DIR}")


if __name__ == "__main__":
    generate_pdfs()
