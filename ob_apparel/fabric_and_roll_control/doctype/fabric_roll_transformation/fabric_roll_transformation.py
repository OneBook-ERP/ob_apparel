import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

class FabricRollTransformation(Document):
    def validate(self):
        if not self.parent_roll:
            frappe.throw(_("Parent Roll is required for transformation."))
        
        parent = frappe.db.get_value("Fabric Roll", self.parent_roll, ["net_weight_kg", "length_meters", "fabric_item", "fabric_lot", "current_warehouse"], as_dict=True)
        if not parent:
            frappe.throw(_("Parent Roll {0} not found.").format(self.parent_roll))
        
        self.parent_weight_kg = flt(parent.net_weight_kg)
        self.parent_length_meters = flt(parent.length_meters)

        if not self.child_rolls:
            frappe.throw(_("At least one child roll must be generated."))

        # Mass Balance Law: Sum of child weights + cutting loss == parent weight (+- 0.5%)
        child_sum = sum(flt(c.net_weight_kg) for c in self.child_rolls)
        total_accounted = child_sum + flt(self.cutting_loss_kg)
        
        diff = abs(total_accounted - self.parent_weight_kg)
        allowed_tolerance = self.parent_weight_kg * 0.005  # 0.5% tolerance
        if diff > allowed_tolerance:
            frappe.throw(_("Mass balance violation: Total child weight ({0}kg) + loss ({1}kg) does not equal parent roll weight ({2}kg).").format(
                round(child_sum, 3), round(flt(self.cutting_loss_kg), 3), round(self.parent_weight_kg, 3)
            ))

    def on_submit(self):
        # Concurrency safety: acquire lock on parent roll
        parent = frappe.db.sql(
            "SELECT name, status, root_roll_id, fabric_item, fabric_lot, current_warehouse FROM `tabFabric Roll` WHERE name=%s FOR UPDATE",
            self.parent_roll,
            as_dict=True
        )
        if not parent:
            frappe.throw(_("Parent roll {0} locked or deleted.").format(self.parent_roll))

        # Retire parent roll
        frappe.db.set_value("Fabric Roll", self.parent_roll, "status", "Consumed")

        root_id = parent[0].root_roll_id or self.parent_roll
        # Create child rolls with genealogy
        for c in self.child_rolls:
            if not frappe.db.exists("Fabric Roll", c.child_barcode):
                child = frappe.get_doc({
                    "doctype": "Fabric Roll",
                    "roll_barcode": c.child_barcode,
                    "fabric_item": parent[0].fabric_item,
                    "fabric_lot": parent[0].fabric_lot,
                    "net_weight_kg": c.net_weight_kg,
                    "length_meters": c.length_meters,
                    "measured_gsm": c.measured_gsm,
                    "cuttable_width_cm": c.cuttable_width_cm,
                    "qc_grade": c.allocated_grade or "Grade A",
                    "status": "Available",
                    "current_warehouse": parent[0].current_warehouse,
                    "parent_roll_id": self.parent_roll,
                    "root_roll_id": root_id
                })
                child.insert(ignore_permissions=True)
