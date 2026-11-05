import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

class RollRemnant(Document):
    def validate(self):
        length = flt(self.remnant_length_meters)
        if length <= 0.0:
            frappe.throw(_("Remnant length must be greater than zero."))
        if length >= 5.0:
            frappe.msgprint(_("Notice: Remnant length is {0}m. Standard remnant policy applies to off-cuts under 5m.").format(length))

    def on_submit(self):
        if self.original_roll:
            frappe.db.set_value("Fabric Roll", self.original_roll, "status", "Remnant")
