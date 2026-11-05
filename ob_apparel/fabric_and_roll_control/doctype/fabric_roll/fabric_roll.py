import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

class FabricRoll(Document):
    def validate(self):
        gross = flt(self.gross_weight_kg)
        tare = flt(self.tare_weight_kg)
        if gross > 0:
            self.net_weight_kg = round(max(0.0, gross - tare), 3)

        if flt(self.net_weight_kg) <= 0.0:
            frappe.throw(_("Net Weight (kg) must be greater than zero."))
        if flt(self.length_meters) <= 0.0:
            frappe.throw(_("Length (meters) must be greater than zero."))

        if not self.root_roll_id:
            self.root_roll_id = self.parent_roll_id or self.name

    @staticmethod
    def acquire_lock(roll_barcode):
        """Row-level lock to prevent concurrent consumption or double lay allocation."""
        return frappe.db.sql(
            "SELECT name, status, qc_grade, current_warehouse FROM `tabFabric Roll` WHERE name=%s FOR UPDATE",
            roll_barcode,
            as_dict=True
        )
