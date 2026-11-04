import os
import csv
import frappe
from frappe.utils import flt

def get_csv_rows(filename):
    path = os.path.join(frappe.get_app_path("ob_apparel"), "seed_data", filename)
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

def load_all_seeds():
    print("Loading TM01 Master Seed Data...")
    load_textile_settings()
    load_fibre_types()
    load_yarn_counts()
    load_fabric_types()
    load_shades()
    load_processes()
    load_textile_uoms()
    load_textile_roles()
    load_yarn_blends()
    load_machines()
    load_shifts()
    load_fabric_constructions()
    frappe.db.commit()
    print("All TM01 Seeds Loaded Successfully!")

def load_machines():
    machines = [
        {"machine_code": "KNIT-01", "machine_name": "Mayer & Cie Circular Knitting 30 Inch", "machine_type": "Circular Knitting", "capacity_per_shift": 450.0},
        {"machine_code": "STENTER-01", "machine_name": "Monforts 8-Chamber Stenter Frame", "machine_type": "Stenter Frame", "capacity_per_shift": 12000.0},
        {"machine_code": "CUT-AUTO-01", "machine_name": "Lectra Vector Automatic Cutter", "machine_type": "Automatic Cutter", "capacity_per_shift": 3500.0},
    ]
    for m in machines:
        if not frappe.db.exists("Machine Master", m["machine_code"]):
            doc = frappe.get_doc({
                "doctype": "Machine Master",
                "machine_code": m["machine_code"],
                "machine_name": m["machine_name"],
                "machine_type": m["machine_type"],
                "capacity_per_shift": m["capacity_per_shift"]
            })
            doc.insert(ignore_permissions=True)
    print(f"  -> {len(machines)} Machines verified.")

def load_shifts():
    shifts = [
        {"shift_code": "SHIFT-A", "shift_name": "Morning Shift (06:00 - 14:00)", "start_time": "06:00:00", "end_time": "14:00:00", "break_duration_minutes": 30},
        {"shift_code": "SHIFT-B", "shift_name": "Evening Shift (14:00 - 22:00)", "start_time": "14:00:00", "end_time": "22:00:00", "break_duration_minutes": 30},
        {"shift_code": "SHIFT-C", "shift_name": "Night Shift (22:00 - 06:00)", "start_time": "22:00:00", "end_time": "06:00:00", "break_duration_minutes": 30},
    ]
    for s in shifts:
        if not frappe.db.exists("Shift Master", s["shift_code"]):
            doc = frappe.get_doc({
                "doctype": "Shift Master",
                "shift_code": s["shift_code"],
                "shift_name": s["shift_name"],
                "start_time": s["start_time"],
                "end_time": s["end_time"],
                "break_duration_minutes": s["break_duration_minutes"]
            })
            doc.insert(ignore_permissions=True)
    print(f"  -> {len(shifts)} Shifts verified.")

def load_fabric_constructions():
    constructions = [
        {
            "construction_code": "SJ-160-COT",
            "construction_name": "Single Jersey 160 GSM 100% Cotton",
            "fabric_type": "SJ",
            "structure_type": "Knit",
            "wales_per_inch": 32.0,
            "courses_per_inch": 42.0,
            "gauge": "24 GG",
            "loop_length_mm": 2.85,
            "theoretical_gsm": 160.0,
            "yarn_components": [{"yarn_count": "30S_NE", "yarn_blend": "100_COT", "yarn_purpose": "Ground", "composition_percent": 100.0}]
        },
        {
            "construction_code": "TWILL-240-WOV",
            "construction_name": "Cotton Twill 2/1 240 GSM",
            "fabric_type": "TWILL",
            "structure_type": "Woven",
            "warp_count": "20S_NE",
            "weft_count": "20S_NE",
            "epi": 108.0,
            "ppi": 56.0,
            "theoretical_gsm": 209.92,
            "yarn_components": [{"yarn_count": "20S_NE", "yarn_blend": "100_COT", "yarn_purpose": "Warp", "composition_percent": 100.0}]
        }
    ]
    for c in constructions:
        if not frappe.db.exists("Fabric Construction", c["construction_code"]):
            doc = frappe.get_doc({
                "doctype": "Fabric Construction",
                "construction_code": c["construction_code"],
                "construction_name": c["construction_name"],
                "fabric_type": c["fabric_type"],
                "structure_type": c["structure_type"],
                "wales_per_inch": c.get("wales_per_inch"),
                "courses_per_inch": c.get("courses_per_inch"),
                "gauge": c.get("gauge"),
                "loop_length_mm": c.get("loop_length_mm"),
                "warp_count": c.get("warp_count"),
                "weft_count": c.get("weft_count"),
                "epi": c.get("epi"),
                "ppi": c.get("ppi"),
                "theoretical_gsm": c.get("theoretical_gsm"),
                "yarn_components": c.get("yarn_components")
            })
            doc.insert(ignore_permissions=True)
    print(f"  -> {len(constructions)} Fabric Constructions verified.")

def load_textile_settings():
    settings = frappe.get_single("Textile Settings")
    settings.min_relaxation_hours = 24.0
    settings.weight_tolerance_percentage = 3.0
    settings.astm_penalty_1pt_max_inches = 3.0
    settings.astm_penalty_2pt_max_inches = 6.0
    settings.astm_penalty_3pt_max_inches = 9.0
    settings.continuous_defect_threshold_meters = 3.0
    settings.grade_a_max_points = 28.0
    settings.grade_b_max_points = 40.0
    settings.auto_roll_barcode = 1
    settings.roll_barcode_prefix = "ROLL-"
    settings.bundle_barcode_prefix = "BNDL-"
    settings.save(ignore_permissions=True)
    print("  -> Textile Settings initialized.")

def load_fibre_types():
    rows = get_csv_rows("fibre_type.csv")
    for r in rows:
        if not frappe.db.exists("Fibre Type", r["fibre_code"]):
            doc = frappe.get_doc({
                "doctype": "Fibre Type",
                "fibre_code": r["fibre_code"],
                "fibre_name": r["fibre_name"],
                "fibre_category": r["fibre_category"],
                "density_g_cm3": flt(r["density_g_cm3"]),
                "standard_moisture_regain_percent": flt(r["standard_moisture_regain_percent"]),
                "hs_code": r["hs_code"]
            })
            doc.insert(ignore_permissions=True)
    print(f"  -> {len(rows)} Fibre Types verified.")

def load_yarn_counts():
    rows = get_csv_rows("yarn_count_master.csv")
    for r in rows:
        if not frappe.db.exists("Yarn Count Master", r["count_code"]):
            doc = frappe.get_doc({
                "doctype": "Yarn Count Master",
                "count_code": r["count_code"],
                "count_name": r["count_name"],
                "count_system": r["count_system"],
                "nominal_value": flt(r["nominal_value"]),
                "is_active": 1
            })
            doc.insert(ignore_permissions=True)
    print(f"  -> {len(rows)} Yarn Counts verified.")

def load_fabric_types():
    rows = get_csv_rows("fabric_type.csv")
    for r in rows:
        if not frappe.db.exists("Fabric Type", r["fabric_type_code"]):
            doc = frappe.get_doc({
                "doctype": "Fabric Type",
                "fabric_type_code": r["fabric_type_code"],
                "fabric_type_name": r["fabric_type_name"],
                "category": r["category"],
                "default_relaxation_hours": flt(r["default_relaxation_hours"])
            })
            doc.insert(ignore_permissions=True)
    print(f"  -> {len(rows)} Fabric Types verified.")

def load_shades():
    rows = get_csv_rows("shade_master.csv")
    for r in rows:
        if not frappe.db.exists("Shade Master", r["shade_code"]):
            doc = frappe.get_doc({
                "doctype": "Shade Master",
                "shade_code": r["shade_code"],
                "shade_name": r["shade_name"],
                "pantone_code": r["pantone_code"],
                "hex_color": r["hex_color"],
                "dye_class": r["dye_class"]
            })
            doc.insert(ignore_permissions=True)
    print(f"  -> {len(rows)} Shades verified.")

def load_processes():
    rows = get_csv_rows("process_master.csv")
    for r in rows:
        if not frappe.db.exists("Process Master", r["process_code"]):
            doc = frappe.get_doc({
                "doctype": "Process Master",
                "process_code": r["process_code"],
                "process_name": r["process_name"],
                "process_stage": r["process_stage"],
                "wet_or_dry": r["wet_or_dry"],
                "standard_loss_cap_percent": flt(r["standard_loss_cap_percent"])
            })
            doc.insert(ignore_permissions=True)
    print(f"  -> {len(rows)} Processes verified.")

def load_textile_uoms():
    rows = get_csv_rows("textile_uom.csv")
    for r in rows:
        if not frappe.db.exists("Textile UOM", r["uom_code"]):
            doc = frappe.get_doc({
                "doctype": "Textile UOM",
                "uom_code": r["uom_code"],
                "uom_name": r["uom_name"],
                "uom_type": r["uom_type"],
                "precision": int(r["precision"])
            })
            doc.insert(ignore_permissions=True)
    print(f"  -> {len(rows)} Textile UOMs verified.")

def load_textile_roles():
    rows = get_csv_rows("textile_role.csv")
    for r in rows:
        if not frappe.db.exists("Textile Role", r["role_code"]):
            doc = frappe.get_doc({
                "doctype": "Textile Role",
                "role_code": r["role_code"],
                "role_name": r["role_name"],
                "can_override_qc_hold": int(r["can_override_qc_hold"]),
                "can_approve_cut_plan": int(r["can_approve_cut_plan"])
            })
            doc.insert(ignore_permissions=True)
    print(f"  -> {len(rows)} Textile Roles verified.")

def load_yarn_blends():
    blends = [
        {
            "blend_code": "100_COT",
            "blend_name": "100% Combed Cotton",
            "components": [{"fibre_type": "COT", "percentage": 100.0}]
        },
        {
            "blend_code": "CP_60_40",
            "blend_name": "60/40 Cotton Polyester Blend",
            "components": [{"fibre_type": "COT", "percentage": 60.0}, {"fibre_type": "POLY", "percentage": 40.0}]
        },
        {
            "blend_code": "COT_ELAS_95_5",
            "blend_name": "95/5 Cotton Spandex / Lycra",
            "components": [{"fibre_type": "COT", "percentage": 95.0}, {"fibre_type": "ELAS", "percentage": 5.0}]
        }
    ]
    for b in blends:
        if not frappe.db.exists("Yarn Blend Master", b["blend_code"]):
            doc = frappe.get_doc({
                "doctype": "Yarn Blend Master",
                "blend_code": b["blend_code"],
                "blend_name": b["blend_name"],
                "is_active": 1,
                "components": b["components"]
            })
            doc.insert(ignore_permissions=True)
    print(f"  -> {len(blends)} Yarn Blends verified.")
