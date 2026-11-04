import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

class FabricType(Document):
    def validate(self):
        if flt(self.default_relaxation_hours) < 12.0:
            frappe.throw(_("Default Relaxation Hours cannot be less than 12.0 hours (Compliance Gate)."))
