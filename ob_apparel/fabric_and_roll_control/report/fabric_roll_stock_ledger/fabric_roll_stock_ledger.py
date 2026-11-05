import frappe
from frappe import _

def execute(filters=None):
    columns = [
        {"label": _("Roll Barcode"), "fieldname": "name", "fieldtype": "Link", "options": "Fabric Roll", "width": 150},
        {"label": _("Fabric Item"), "fieldname": "fabric_item", "fieldtype": "Link", "options": "Fabric Item", "width": 180},
        {"label": _("Fabric Lot"), "fieldname": "fabric_lot", "fieldtype": "Link", "options": "Fabric Lot", "width": 140},
        {"label": _("Warehouse"), "fieldname": "current_warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 160},
        {"label": _("Rack Location"), "fieldname": "rack_location", "fieldtype": "Data", "width": 130},
        {"label": _("Net Wt (kg)"), "fieldname": "net_weight_kg", "fieldtype": "Float", "width": 120},
        {"label": _("Length (m)"), "fieldname": "length_meters", "fieldtype": "Float", "width": 110},
        {"label": _("GSM"), "fieldname": "measured_gsm", "fieldtype": "Float", "width": 90},
        {"label": _("QC Grade"), "fieldname": "qc_grade", "fieldtype": "Data", "width": 120},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 110},
    ]

    conditions = {}
    if filters:
        if filters.get("warehouse"):
            conditions["current_warehouse"] = filters.get("warehouse")
        if filters.get("qc_grade"):
            conditions["qc_grade"] = filters.get("qc_grade")
        if filters.get("status"):
            conditions["status"] = filters.get("status")

    rolls = frappe.get_all(
        "Fabric Roll",
        filters=conditions,
        fields=["name", "fabric_item", "fabric_lot", "current_warehouse", "rack_location", "net_weight_kg", "length_meters", "measured_gsm", "qc_grade", "status"],
        order_by="creation desc"
    )

    data = []
    for r in rolls:
        data.append({
            "name": r.name,
            "fabric_item": r.fabric_item,
            "fabric_lot": r.fabric_lot,
            "current_warehouse": r.current_warehouse,
            "rack_location": r.rack_location,
            "net_weight_kg": r.net_weight_kg,
            "length_meters": r.length_meters,
            "measured_gsm": r.measured_gsm,
            "qc_grade": r.qc_grade,
            "status": r.status
        })

    return columns, data
