import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

class YarnBlendMaster(Document):
    def validate(self):
        if not self.components:
            frappe.throw(_("At least one fibre component must be specified."))
        
        seen_fibres = set()
        total_pct = 0.0
        for item in self.components:
            if item.fibre_type in seen_fibres:
                frappe.throw(_("Duplicate fibre type {0} in blend components.").format(item.fibre_type))
            seen_fibres.add(item.fibre_type)
            pct = flt(item.percentage)
            if pct <= 0.0:
                frappe.throw(_("Component percentage must be greater than zero for {0}.").format(item.fibre_type))
            total_pct += pct

        if abs(total_pct - 100.0) > 0.01:
            frappe.throw(_("Total fibre blend percentage must equal exactly 100.0%. Current sum: {0}%").format(round(total_pct, 2)))
