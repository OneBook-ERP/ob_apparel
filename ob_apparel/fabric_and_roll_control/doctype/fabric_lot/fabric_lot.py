import frappe
from frappe.model.document import Document
from frappe.utils import flt

class FabricLot(Document):
    def update_totals(self):
        rolls = frappe.get_all(
            "Fabric Roll",
            filters={"fabric_lot": self.name, "status": ["!=", "Scrapped"]},
            fields=["net_weight_kg", "length_meters", "measured_gsm"]
        )
        self.total_rolls = len(rolls)
        self.total_weight_kg = round(sum(flt(r.net_weight_kg) for r in rolls), 2)
        self.total_length_meters = round(sum(flt(r.length_meters) for r in rolls), 2)
        if self.total_rolls > 0:
            self.average_gsm = round(sum(flt(r.measured_gsm) for r in rolls) / self.total_rolls, 2)
        else:
            self.average_gsm = 0.0
        self.save(ignore_permissions=True)
