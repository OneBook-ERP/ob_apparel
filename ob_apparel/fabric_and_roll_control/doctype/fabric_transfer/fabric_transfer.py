import frappe
from frappe import _
from frappe.model.document import Document

class FabricTransfer(Document):
    def validate(self):
        if not self.rolls:
            frappe.throw(_("At least one roll must be selected for transfer."))
        if self.from_warehouse == self.to_warehouse:
            frappe.throw(_("Source and Target warehouse cannot be the same."))

    def on_submit(self):
        # Concurrency safety: acquire row lock and update warehouse
        for r in self.rolls:
            locked = frappe.db.sql(
                "SELECT name, status, current_warehouse FROM `tabFabric Roll` WHERE name=%s FOR UPDATE",
                r.roll_barcode,
                as_dict=True
            )
            if not locked:
                frappe.throw(_("Fabric Roll {0} does not exist.").format(r.roll_barcode))
            
            new_status = locked[0].status
            if self.purpose == "Move to Relaxation":
                new_status = "Reserved"
            elif self.purpose == "Issue to Cutting Table":
                new_status = "In Spreading"
            elif self.purpose == "Return to Store":
                new_status = "Available"

            frappe.db.set_value("Fabric Roll", r.roll_barcode, {
                "current_warehouse": self.to_warehouse,
                "rack_location": self.target_rack_location or r.rack_location,
                "status": new_status
            })
