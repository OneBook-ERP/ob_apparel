import frappe
from frappe.model.document import Document

class MachineMaster(Document):
    def validate(self):
        if not self.machine_barcode and self.machine_code:
            self.machine_barcode = f"MC-{self.machine_code}"
