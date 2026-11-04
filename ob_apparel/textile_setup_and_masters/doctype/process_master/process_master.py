import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

class ProcessMaster(Document):
    def validate(self):
        loss = flt(self.standard_loss_cap_percent)
        if loss < 0.0 or loss > 25.0:
            frappe.throw(_("Standard process loss cap must be between 0% and 25%."))
