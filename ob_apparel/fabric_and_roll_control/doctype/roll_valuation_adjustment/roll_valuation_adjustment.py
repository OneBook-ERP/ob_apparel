import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

class RollValuationAdjustment(Document):
    def validate(self):
        orig = flt(self.original_rate_per_kg)
        deval = flt(self.devalued_rate_per_kg)
        if deval >= orig:
            frappe.throw(_("Devalued Rate must be strictly lower than Original Rate."))
        
        roll_wt = flt(frappe.db.get_value("Fabric Roll", self.fabric_roll, "net_weight_kg") or 0.0)
        self.variance_amount = round((orig - deval) * roll_wt, 2)

    def on_submit(self):
        if self.fabric_roll and self.downgraded_grade:
            frappe.db.set_value("Fabric Roll", self.fabric_roll, "qc_grade", self.downgraded_grade)
