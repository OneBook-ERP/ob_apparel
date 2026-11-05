import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

class FabricInward(Document):
    def validate(self):
        invoiced = flt(self.mill_invoiced_weight_kg)
        scale = flt(self.physical_scale_weight_kg)
        
        if invoiced <= 0.0:
            frappe.throw(_("Mill Invoiced Weight must be greater than zero."))
        if scale <= 0.0:
            frappe.throw(_("Physical Scale Weight must be greater than zero."))

        diff = scale - invoiced
        var_pct = round((diff / invoiced) * 100.0, 2)
        self.weight_variance_kg = round(diff, 3)
        self.weight_variance_percent = var_pct

        # CMP-02 / G2 Hard Gate: Check weight tolerance
        settings_tolerance = flt(frappe.db.get_single_value("Textile Settings", "weight_tolerance_percentage") or 3.0)
        if abs(var_pct) > settings_tolerance:
            self.variance_status = "Excess Deviation Alert"
        else:
            self.variance_status = "Within Tolerance"

        if not self.rolls:
            frappe.throw(_("At least one roll must be specified in the rolls table."))

    def on_submit(self):
        # Auto-create Fabric Roll records in Quarantine status
        for r in self.rolls:
            if not frappe.db.exists("Fabric Roll", r.roll_barcode):
                roll = frappe.get_doc({
                    "doctype": "Fabric Roll",
                    "roll_barcode": r.roll_barcode,
                    "fabric_item": r.fabric_item,
                    "fabric_lot": r.fabric_lot,
                    "net_weight_kg": r.net_weight_kg,
                    "length_meters": r.length_meters,
                    "measured_gsm": r.measured_gsm,
                    "cuttable_width_cm": r.cuttable_width_cm,
                    "current_warehouse": self.default_warehouse,
                    "rack_location": r.rack_location,
                    "status": "Quarantine",
                    "qc_grade": "Quarantine"
                })
                roll.insert(ignore_permissions=True)
