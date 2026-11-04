import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

class TextileSettings(Document):
    def validate(self):
        if flt(self.min_relaxation_hours) < 12.0:
            frappe.throw(_("Minimum Relaxation Hours cannot be less than 12.0 hours (Compliance Gate)."))
        if flt(self.weight_tolerance_percentage) > 5.0:
            frappe.throw(_("Weight Tolerance Percentage cannot exceed 5.0%."))
        if flt(self.weight_tolerance_percentage) < 0.0:
            frappe.throw(_("Weight Tolerance Percentage cannot be negative."))
        if flt(self.grade_a_max_points) >= flt(self.grade_b_max_points):
            frappe.throw(_("Grade A Max Points must be strictly less than Grade B Max Points."))
