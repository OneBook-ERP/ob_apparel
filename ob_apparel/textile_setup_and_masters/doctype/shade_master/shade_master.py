import re
import frappe
from frappe import _
from frappe.model.document import Document

class ShadeMaster(Document):
    def validate(self):
        if self.pantone_code:
            code = self.pantone_code.strip()
            if not re.match(r"^\d{2}-\d{4}\s*(TCX|TPX|tcx|tpx)$", code):
                frappe.throw(_("Invalid Pantone Code format '{0}'. Must follow standard syntax like '19-4010 TCX' or '11-0601 TPX'.").format(code))
