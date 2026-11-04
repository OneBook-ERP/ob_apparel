from datetime import datetime
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

class ShiftMaster(Document):
    def validate(self):
        if self.start_time and self.end_time:
            s_parts = str(self.start_time).split(":")
            e_parts = str(self.end_time).split(":")
            t1 = datetime(2000, 1, 1, int(s_parts[0]), int(s_parts[1]), int(s_parts[2]) if len(s_parts) > 2 else 0)
            t2 = datetime(2000, 1, 1, int(e_parts[0]), int(e_parts[1]), int(e_parts[2]) if len(e_parts) > 2 else 0)
            
            diff = (t2 - t1).total_seconds() / 3600.0
            if diff < 0:
                diff += 24.0
            
            break_hrs = flt(self.break_duration_minutes) / 60.0
            self.working_hours = round(max(0.0, diff - break_hrs), 2)
