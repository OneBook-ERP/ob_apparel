import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

class YarnCountMaster(Document):
    def validate(self):
        val = flt(self.nominal_value)
        if val <= 0.0:
            frappe.throw(_("Nominal Count Value must be greater than zero."))
        self.calculate_conversions()

    def calculate_conversions(self):
        val = flt(self.nominal_value)
        system = self.count_system

        if system == "English Cotton Count (Ne)":
            self.english_cotton_count_ne = val
            self.denier = round(5315.0 / val, 2)
            self.tex = round(590.5 / val, 2)
            self.metric_count_nm = round(1.693 * val, 2)
        elif system == "Denier (D)":
            self.denier = val
            self.english_cotton_count_ne = round(5315.0 / val, 2)
            self.tex = round(val / 9.0, 2)
            self.metric_count_nm = round(9000.0 / val, 2)
        elif system == "Tex":
            self.tex = val
            self.english_cotton_count_ne = round(590.5 / val, 2)
            self.denier = round(val * 9.0, 2)
            self.metric_count_nm = round(1000.0 / val, 2)
        elif system == "Metric Count (Nm)":
            self.metric_count_nm = val
            self.english_cotton_count_ne = round(val / 1.693, 2)
            self.denier = round(9000.0 / val, 2)
            self.tex = round(1000.0 / val, 2)
