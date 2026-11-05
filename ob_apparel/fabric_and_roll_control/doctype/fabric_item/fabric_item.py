import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

class FabricItem(Document):
    def validate(self):
        width = flt(self.cuttable_width_cm)
        if width <= 0.0:
            frappe.throw(_("Cuttable Width must be greater than zero."))
        
        # Tubular fabrics auto-double cuttable width for marker yield math
        if self.is_tubular:
            self.effective_marker_width_cm = round(width * 2.0, 2)
        else:
            self.effective_marker_width_cm = round(width, 2)
