import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

class FabricConstruction(Document):
    def validate(self):
        self.calculate_theoretical_gsm()
        if self.yarn_components:
            total = sum(flt(c.composition_percent) for c in self.yarn_components)
            if abs(total - 100.0) > 0.01:
                frappe.throw(_("Total yarn component composition must equal 100.0%. Current sum: {0}%").format(round(total, 2)))

    def calculate_theoretical_gsm(self):
        if self.structure_type == "Woven" and self.warp_count and self.weft_count and self.epi and self.ppi:
            warp_ne = frappe.db.get_value("Yarn Count Master", self.warp_count, "english_cotton_count_ne")
            weft_ne = frappe.db.get_value("Yarn Count Master", self.weft_count, "english_cotton_count_ne")
            if warp_ne and weft_ne and flt(warp_ne) > 0 and flt(weft_ne) > 0:
                self.theoretical_gsm = round(((flt(self.epi) / flt(warp_ne)) + (flt(self.ppi) / flt(weft_ne))) * 25.6, 2)
