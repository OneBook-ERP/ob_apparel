import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

class FibreType(Document):
    def validate(self):
        if flt(self.density_g_cm3) <= 0.0:
            frappe.throw(_("Density must be greater than zero."))
        if flt(self.standard_moisture_regain_percent) < 0.0:
            frappe.throw(_("Standard moisture regain percentage cannot be negative."))
