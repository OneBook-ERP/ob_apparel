import frappe
from frappe import _

def execute(filters=None):
    columns = [
        {"label": _("Master Category"), "fieldname": "category", "fieldtype": "Data", "width": 180},
        {"label": _("DocType Name"), "fieldname": "doctype_name", "fieldtype": "Link", "options": "DocType", "width": 200},
        {"label": _("Configured Count"), "fieldname": "count", "fieldtype": "Int", "width": 140},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 140},
        {"label": _("Readiness Impact"), "fieldname": "impact", "fieldtype": "Data", "width": 300},
    ]

    doctypes_to_audit = [
        ("System Configuration", "Textile Settings", "Global parameters (ASTM, relaxation, tolerances)"),
        ("Raw Materials", "Fibre Type", "Fibre catalog and density parameters"),
        ("Raw Materials", "Yarn Count Master", "Count definitions and conversions"),
        ("Raw Materials", "Yarn Blend Master", "Standard fibre blends (100% balance)"),
        ("Fabric Masters", "Fabric Type", "Knit/woven types and relaxation hours"),
        ("Fabric Masters", "Fabric Construction", "Structural specs and theoretical GSM"),
        ("Color Authority", "Shade Master", "Pantone codes and RGB previews"),
        ("Operations", "Process Master", "Textile wet/dry processes and loss caps"),
        ("Floor Assets", "Machine Master", "Floor machines with barcodes"),
        ("HR & Floor Shifts", "Shift Master", "Shift hours and timings"),
        ("UOM Standard", "Textile UOM", "Cones, Rolls, Bales, Thans precision"),
        ("Permissions & Roles", "Textile Role", "Factory roles and anti-bypass SoD"),
    ]

    data = []
    total_configured = 0
    total_checks = len(doctypes_to_audit)

    for cat, dt, impact in doctypes_to_audit:
        try:
            if dt == "Textile Settings":
                val = frappe.db.get_single_value("Textile Settings", "min_relaxation_hours")
                cnt = 1 if val else 0
            else:
                cnt = frappe.db.count(dt)
        except Exception:
            cnt = 0

        status = "Ready" if cnt > 0 else "Missing Data"
        if cnt > 0:
            total_configured += 1

        data.append({
            "category": cat,
            "doctype_name": dt,
            "count": cnt,
            "status": status,
            "impact": impact
        })

    readiness_pct = round((total_configured / total_checks) * 100.0, 1)

    report_summary = [
        {
            "value": f"{readiness_pct}%",
            "indicator": "Green" if readiness_pct >= 80 else ("Orange" if readiness_pct >= 40 else "Red"),
            "label": _("System Setup Readiness"),
            "datatype": "Percent"
        },
        {
            "value": total_configured,
            "indicator": "Blue",
            "label": _("Configured Masters"),
            "datatype": "Int"
        },
        {
            "value": total_checks - total_configured,
            "indicator": "Red" if total_checks - total_configured > 0 else "Green",
            "label": _("Pending Masters"),
            "datatype": "Int"
        }
    ]

    return columns, data, None, None, report_summary
