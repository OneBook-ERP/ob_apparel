import frappe
from frappe import _
from frappe.model.document import Document

class TextileUOM(Document):
    def validate(self):
        if self.precision is not None and (int(self.precision) < 0 or int(self.precision) > 4):
            frappe.throw(_("Precision must be between 0 and 4 decimals."))
