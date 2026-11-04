import frappe
from frappe import _

def execute(filters=None):
    columns = [
        {"label": _("Count Code"), "fieldname": "name", "fieldtype": "Link", "options": "Yarn Count Master", "width": 140},
        {"label": _("Count Name"), "fieldname": "count_name", "fieldtype": "Data", "width": 200},
        {"label": _("Primary System"), "fieldname": "count_system", "fieldtype": "Data", "width": 180},
        {"label": _("Nominal Value"), "fieldname": "nominal_value", "fieldtype": "Float", "width": 130},
        {"label": _("Ne (English Count)"), "fieldname": "english_cotton_count_ne", "fieldtype": "Float", "width": 140},
        {"label": _("Denier (D)"), "fieldname": "denier", "fieldtype": "Float", "width": 130},
        {"label": _("Tex"), "fieldname": "tex", "fieldtype": "Float", "width": 120},
        {"label": _("Nm (Metric Count)"), "fieldname": "metric_count_nm", "fieldtype": "Float", "width": 140},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 110},
    ]

    records = frappe.get_all(
        "Yarn Count Master",
        fields=["name", "count_name", "count_system", "nominal_value", "english_cotton_count_ne", "denier", "tex", "metric_count_nm", "is_active"],
        order_by="english_cotton_count_ne desc"
    )

    data = []
    for r in records:
        data.append({
            "name": r.name,
            "count_name": r.count_name,
            "count_system": r.count_system,
            "nominal_value": r.nominal_value,
            "english_cotton_count_ne": r.english_cotton_count_ne,
            "denier": r.denier,
            "tex": r.tex,
            "metric_count_nm": r.metric_count_nm,
            "status": "Active" if r.is_active else "Inactive"
        })

    return columns, data
