import frappe
from frappe import _

def execute(filters=None):
    columns = [
        {"label": _("Inward ID"), "fieldname": "name", "fieldtype": "Link", "options": "Fabric Inward", "width": 160},
        {"label": _("Posting Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 110},
        {"label": _("Supplier"), "fieldname": "supplier", "fieldtype": "Link", "options": "Supplier", "width": 180},
        {"label": _("Mill Challan"), "fieldname": "mill_delivery_note", "fieldtype": "Data", "width": 150},
        {"label": _("Invoiced Wt (kg)"), "fieldname": "mill_invoiced_weight_kg", "fieldtype": "Float", "width": 130},
        {"label": _("Scale Wt (kg)"), "fieldname": "physical_scale_weight_kg", "fieldtype": "Float", "width": 130},
        {"label": _("Variance (kg)"), "fieldname": "weight_variance_kg", "fieldtype": "Float", "width": 120},
        {"label": _("Variance %"), "fieldname": "weight_variance_percent", "fieldtype": "Percent", "width": 110},
        {"label": _("Compliance Status"), "fieldname": "variance_status", "fieldtype": "Data", "width": 160},
    ]

    records = frappe.get_all(
        "Fabric Inward",
        fields=["name", "posting_date", "supplier", "mill_delivery_note", "mill_invoiced_weight_kg", "physical_scale_weight_kg", "weight_variance_kg", "weight_variance_percent", "variance_status"],
        order_by="posting_date desc"
    )

    data = []
    excess_count = 0
    for r in records:
        if r.variance_status == "Excess Deviation Alert":
            excess_count += 1
        data.append({
            "name": r.name,
            "posting_date": r.posting_date,
            "supplier": r.supplier,
            "mill_delivery_note": r.mill_delivery_note,
            "mill_invoiced_weight_kg": r.mill_invoiced_weight_kg,
            "physical_scale_weight_kg": r.physical_scale_weight_kg,
            "weight_variance_kg": r.weight_variance_kg,
            "weight_variance_percent": r.weight_variance_percent,
            "variance_status": r.variance_status
        })

    report_summary = [
        {
            "value": len(records),
            "indicator": "Blue",
            "label": _("Total Inward Receipts"),
            "datatype": "Int"
        },
        {
            "value": excess_count,
            "indicator": "Red" if excess_count > 0 else "Green",
            "label": _("Deviation Alerts (>3%)"),
            "datatype": "Int"
        }
    ]

    return columns, data, None, None, report_summary
