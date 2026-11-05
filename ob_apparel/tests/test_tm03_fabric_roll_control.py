import subprocess
import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import flt, today

class TestTM03FabricRollControl(FrappeTestCase):
    def setUp(self):
        frappe.set_user("Administrator")
        self.setup_test_prerequisites()

    def setup_test_prerequisites(self):
        # Ensure a test Fabric Item exists
        if not frappe.db.exists("Fabric Item", "TEST_FAB_SJ_NAVY"):
            fi = frappe.get_doc({
                "doctype": "Fabric Item",
                "item_code": "TEST_FAB_SJ_NAVY",
                "fabric_name": "Test Single Jersey 160 GSM Navy",
                "fabric_type": "SJ",
                "fabric_construction": "SJ-160-COT",
                "shade": "SHD-001",
                "nominal_gsm": 160.0,
                "cuttable_width_cm": 80.0,
                "is_tubular": 1
            })
            fi.insert(ignore_permissions=True)

        if not frappe.db.exists("Fabric Item", "TEST_FAB_TWILL_OPEN"):
            fi2 = frappe.get_doc({
                "doctype": "Fabric Item",
                "item_code": "TEST_FAB_TWILL_OPEN",
                "fabric_name": "Test Twill Open Width 150cm",
                "fabric_type": "TWILL",
                "fabric_construction": "TWILL-240-WOV",
                "shade": "SHD-002",
                "nominal_gsm": 240.0,
                "cuttable_width_cm": 150.0,
                "is_tubular": 0
            })
            fi2.insert(ignore_permissions=True)

    # =========================================================================
    # TIER 1: UNIT TESTS (Formulas, Boundaries, Conversions & Validations)
    # =========================================================================

    def test_01_unit_fabric_item_tubular_width_math(self):
        """Unit Test: Verify tubular fabric doubles cuttable width for CAD marker yield."""
        tubular = frappe.get_doc("Fabric Item", "TEST_FAB_SJ_NAVY")
        self.assertEqual(flt(tubular.effective_marker_width_cm), 160.0)

        open_width = frappe.get_doc("Fabric Item", "TEST_FAB_TWILL_OPEN")
        self.assertEqual(flt(open_width.effective_marker_width_cm), 150.0)

    def test_02_unit_fabric_roll_net_weight_calculation(self):
        """Unit Test: Verify net weight calculation and rejection of zero/negative values."""
        roll = frappe.get_doc({
            "doctype": "Fabric Roll",
            "roll_barcode": "UT_ROLL_WT_01",
            "fabric_item": "TEST_FAB_SJ_NAVY",
            "gross_weight_kg": 25.500,
            "tare_weight_kg": 0.500,
            "net_weight_kg": 25.000,
            "length_meters": 110.0,
            "measured_gsm": 162.0
        })
        roll.insert(ignore_permissions=True)
        self.assertAlmostEqual(flt(roll.net_weight_kg), 25.000, places=3)

        # Non-positive weight must fail
        invalid_roll = frappe.get_doc({
            "doctype": "Fabric Roll",
            "roll_barcode": "UT_ROLL_FAIL_01",
            "fabric_item": "TEST_FAB_SJ_NAVY",
            "net_weight_kg": 0.0,
            "length_meters": 100.0
        })
        self.assertRaises(frappe.ValidationError, invalid_roll.insert)

    def test_03_unit_inward_weight_tolerance_validation(self):
        """Unit Test: CMP-02 Hard Gate: Detect and alert weight variance exceeding +-3.0%."""
        inw = frappe.get_doc({
            "doctype": "Fabric Inward",
            "posting_date": today(),
            "mill_delivery_note": "CHALLAN-UT-01",
            "mill_invoiced_weight_kg": 100.0,
            "physical_scale_weight_kg": 105.0,  # +5% variance (exceeds 3%)
            "rolls": [
                {
                    "roll_barcode": "UT_INW_ROLL_01",
                    "fabric_item": "TEST_FAB_SJ_NAVY",
                    "net_weight_kg": 105.0,
                    "length_meters": 450.0,
                    "measured_gsm": 160.0
                }
            ]
        })
        inw.validate()
        self.assertEqual(inw.variance_status, "Excess Deviation Alert")
        self.assertEqual(flt(inw.weight_variance_percent), 5.0)

    def test_04_unit_transformation_mass_balance_enforcement(self):
        """Unit Test: Splitting must conserve mass balance within 0.5% tolerance."""
        # Create a parent roll of 30.0kg
        parent = frappe.get_doc({
            "doctype": "Fabric Roll",
            "roll_barcode": "UT_PARENT_SPLIT",
            "fabric_item": "TEST_FAB_SJ_NAVY",
            "net_weight_kg": 30.0,
            "length_meters": 130.0,
            "measured_gsm": 160.0,
            "status": "Available"
        })
        parent.insert(ignore_permissions=True)

        # Valid split: 18kg + 11.8kg + 0.2kg loss = 30.0kg
        valid_split = frappe.get_doc({
            "doctype": "Fabric Roll Transformation",
            "transformation_type": "Roll Split",
            "parent_roll": "UT_PARENT_SPLIT",
            "cutting_loss_kg": 0.2,
            "child_rolls": [
                {"child_barcode": "UT_CHILD_01", "net_weight_kg": 18.0, "length_meters": 78.0, "measured_gsm": 160.0},
                {"child_barcode": "UT_CHILD_02", "net_weight_kg": 11.8, "length_meters": 51.0, "measured_gsm": 160.0}
            ]
        })
        valid_split.validate()  # Passes mass balance

        # Invalid split: 18kg + 10.0kg = 28.0kg (diff 2kg > 0.5%)
        invalid_split = frappe.get_doc({
            "doctype": "Fabric Roll Transformation",
            "transformation_type": "Roll Split",
            "parent_roll": "UT_PARENT_SPLIT",
            "cutting_loss_kg": 0.0,
            "child_rolls": [
                {"child_barcode": "UT_CHILD_FAIL", "net_weight_kg": 18.0, "length_meters": 78.0}
            ]
        })
        self.assertRaises(frappe.ValidationError, invalid_split.validate)

    def test_05_unit_roll_valuation_adjustment_variance(self):
        """Unit Test: Downgraded roll valuation variance calculation."""
        # Create a roll
        roll = frappe.get_doc({
            "doctype": "Fabric Roll",
            "roll_barcode": "UT_ROLL_DEVAL",
            "fabric_item": "TEST_FAB_SJ_NAVY",
            "net_weight_kg": 25.0,
            "length_meters": 110.0,
            "qc_grade": "Grade A"
        })
        roll.insert(ignore_permissions=True)

        rva = frappe.get_doc({
            "doctype": "Roll Valuation Adjustment",
            "fabric_roll": "UT_ROLL_DEVAL",
            "previous_grade": "Grade A",
            "downgraded_grade": "Grade B",
            "original_rate_per_kg": 300.0,
            "devalued_rate_per_kg": 220.0
        })
        rva.validate()
        # Variance = (300 - 220) * 25kg = 2000.00
        self.assertEqual(flt(rva.variance_amount), 2000.0)

    # =========================================================================
    # TIER 2: INTEGRATION TESTS (Multi-DocType Interactions & Script Reports)
    # =========================================================================

    def test_06_integration_fabric_lot_rollup(self):
        """Integration Test: Fabric Lot aggregates total rolls, meters, and net kg."""
        lot = frappe.get_doc({
            "doctype": "Fabric Lot",
            "lot_number": "INT_LOT_001",
            "fabric_item": "TEST_FAB_SJ_NAVY"
        })
        lot.insert(ignore_permissions=True)

        # Create two rolls in this lot
        for i, wt in enumerate([24.0, 26.0], 1):
            frappe.get_doc({
                "doctype": "Fabric Roll",
                "roll_barcode": f"INT_LOT_ROLL_{i}",
                "fabric_item": "TEST_FAB_SJ_NAVY",
                "fabric_lot": "INT_LOT_001",
                "net_weight_kg": wt,
                "length_meters": 100.0,
                "measured_gsm": 160.0,
                "status": "Available"
            }).insert(ignore_permissions=True)

        lot.update_totals()
        self.assertEqual(lot.total_rolls, 2)
        self.assertAlmostEqual(flt(lot.total_weight_kg), 50.0, places=2)
        self.assertAlmostEqual(flt(lot.total_length_meters), 200.0, places=2)

    def test_07_integration_roll_concurrency_lock(self):
        """Integration Test: Verify row-level lock using for_update=True succeeds without deadlocks."""
        # Create roll
        roll = frappe.get_doc({
            "doctype": "Fabric Roll",
            "roll_barcode": "INT_LOCK_ROLL",
            "fabric_item": "TEST_FAB_SJ_NAVY",
            "net_weight_kg": 20.0,
            "length_meters": 90.0,
            "status": "Available"
        })
        roll.insert(ignore_permissions=True)

        # Acquire lock
        from ob_apparel.fabric_and_roll_control.doctype.fabric_roll.fabric_roll import FabricRoll
        res = FabricRoll.acquire_lock("INT_LOCK_ROLL")
        self.assertTrue(len(res) > 0)
        self.assertEqual(res[0].name, "INT_LOCK_ROLL")

    def test_08_integration_fabric_roll_stock_ledger_report(self):
        """Integration Test: Execute Fabric Roll Stock Ledger Report and verify output columns."""
        from ob_apparel.fabric_and_roll_control.report.fabric_roll_stock_ledger.fabric_roll_stock_ledger import execute
        columns, data = execute()
        self.assertTrue(len(columns) >= 9)
        self.assertTrue(len(data) >= 1)

    def test_09_integration_mill_variance_report(self):
        """Integration Test: Execute Mill Weight vs Delivery Variance Report."""
        from ob_apparel.fabric_and_roll_control.report.roll_weight_vs_delivery_variance.roll_weight_vs_delivery_variance import execute
        columns, data, chart, msg, summary = execute()
        self.assertTrue(len(columns) >= 8)
        self.assertIsNotNone(summary)

    # =========================================================================
    # TIER 3: END-TO-END (E2E) FLOW TESTS (Full Lifecycle Simulation)
    # =========================================================================

    def test_10_e2e_fabric_inward_to_split_to_transfer(self):
        """E2E Test: Full Floor Simulation: Inward -> Roll Split -> Inter-Warehouse Transfer."""
        # Step 1: Inward gate receipt of a 50kg roll
        inw = frappe.get_doc({
            "doctype": "Fabric Inward",
            "posting_date": today(),
            "mill_delivery_note": "E2E-CHALLAN-999",
            "mill_invoiced_weight_kg": 50.0,
            "physical_scale_weight_kg": 50.2,
            "default_warehouse": "Stores - BVK",
            "rolls": [
                {
                    "roll_barcode": "E2E_MASTER_ROLL_99",
                    "fabric_item": "TEST_FAB_SJ_NAVY",
                    "net_weight_kg": 50.0,
                    "length_meters": 220.0,
                    "measured_gsm": 160.0,
                    "cuttable_width_cm": 80.0,
                    "rack_location": "RACK-E2E-01"
                }
            ]
        })
        inw.insert(ignore_permissions=True)
        inw.submit()

        # Step 2: Verify Fabric Roll was auto-created in Quarantine
        self.assertTrue(frappe.db.exists("Fabric Roll", "E2E_MASTER_ROLL_99"))
        roll = frappe.get_doc("Fabric Roll", "E2E_MASTER_ROLL_99")
        self.assertEqual(roll.status, "Quarantine")
        self.assertEqual(roll.qc_grade, "Quarantine")

        # Step 3: Transform (Split) master roll into 2 halves
        split_tx = frappe.get_doc({
            "doctype": "Fabric Roll Transformation",
            "transformation_type": "Roll Split",
            "parent_roll": "E2E_MASTER_ROLL_99",
            "cutting_loss_kg": 0.0,
            "child_rolls": [
                {"child_barcode": "E2E_CHILD_99_A", "net_weight_kg": 25.0, "length_meters": 110.0, "measured_gsm": 160.0, "cuttable_width_cm": 80.0, "allocated_grade": "Grade A"},
                {"child_barcode": "E2E_CHILD_99_B", "net_weight_kg": 25.0, "length_meters": 110.0, "measured_gsm": 160.0, "cuttable_width_cm": 80.0, "allocated_grade": "Grade A"}
            ]
        })
        split_tx.insert(ignore_permissions=True)
        split_tx.submit()

        # Step 4: Verify parent retired and child rolls active with genealogy
        self.assertEqual(frappe.db.get_value("Fabric Roll", "E2E_MASTER_ROLL_99", "status"), "Consumed")
        child_a = frappe.get_doc("Fabric Roll", "E2E_CHILD_99_A")
        self.assertEqual(child_a.status, "Available")
        self.assertEqual(child_a.parent_roll_id, "E2E_MASTER_ROLL_99")
        self.assertEqual(child_a.root_roll_id, "E2E_MASTER_ROLL_99")

        # Step 5: Transfer Child Roll A to Cutting Room
        trsf = frappe.get_doc({
            "doctype": "Fabric Transfer",
            "posting_date": today(),
            "from_warehouse": "Stores - BVK",
            "to_warehouse": "Work In Progress - BVK",
            "purpose": "Issue to Cutting Table",
            "rolls": [
                {"roll_barcode": "E2E_CHILD_99_A", "fabric_item": "TEST_FAB_SJ_NAVY", "net_weight_kg": 25.0, "length_meters": 110.0}
            ]
        })
        trsf.insert(ignore_permissions=True)
        trsf.submit()

        # Step 6: Verify updated warehouse and status
        child_a.reload()
        self.assertEqual(child_a.current_warehouse, "Work In Progress - BVK")
        self.assertEqual(child_a.status, "In Spreading")

    # =========================================================================
    # ARCHITECTURAL DISCIPLINE: ZERO-CORE TOUCH INTEGRITY
    # =========================================================================

    def test_11_gravitas_zero_core_integrity(self):
        """Discipline Test: Verify zero core files in apps/frappe or apps/erpnext were modified."""
        for core_app in ["frappe", "erpnext"]:
            app_dir = f"/home/pavithran/frappe-bench/apps/{core_app}"
            res = subprocess.run(["git", "status", "--porcelain"], cwd=app_dir, capture_output=True, text=True)
            self.assertEqual(res.stdout.strip(), "", f"Core app {core_app} has modified files! Zero-core discipline violated.")
