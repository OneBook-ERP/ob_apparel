import subprocess
import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import flt

class TestTM01Masters(FrappeTestCase):
    def setUp(self):
        frappe.set_user("Administrator")

    # =========================================================================
    # TIER 1: UNIT TESTS (Field Validations, Boundaries, Regex, Calculations)
    # =========================================================================

    def test_01_unit_textile_settings_boundary_validation(self):
        """Unit Test: Verify Textile Settings boundary constraints (Relaxation >= 12h, Tolerance <= 5%, Grade A < B)."""
        settings = frappe.get_doc("Textile Settings")
        
        # Test 1A: Relaxation Hours < 12h must throw ValidationError
        settings.min_relaxation_hours = 8.0
        self.assertRaises(frappe.ValidationError, settings.save)

        # Test 1B: Weight Tolerance > 5% must throw ValidationError
        settings.reload()
        settings.weight_tolerance_percentage = 8.0
        self.assertRaises(frappe.ValidationError, settings.save)

        # Test 1C: Grade A >= Grade B must throw ValidationError
        settings.reload()
        settings.grade_a_max_points = 45.0
        settings.grade_b_max_points = 40.0
        self.assertRaises(frappe.ValidationError, settings.save)

    def test_02_unit_yarn_count_math_conversions(self):
        """Unit Test: Verify mathematical conversion formulas between Ne, Denier, Tex, and Nm."""
        # 2A: English Cotton Count (Ne) System
        count_ne = frappe.get_doc({
            "doctype": "Yarn Count Master",
            "count_code": "UT_30S_NE",
            "count_name": "Unit Test 30s Ne",
            "count_system": "English Cotton Count (Ne)",
            "nominal_value": 30.0
        })
        count_ne.insert(ignore_permissions=True)
        self.assertEqual(flt(count_ne.english_cotton_count_ne), 30.0)
        self.assertAlmostEqual(flt(count_ne.denier), 177.17, places=1)
        self.assertAlmostEqual(flt(count_ne.tex), 19.68, places=1)
        self.assertAlmostEqual(flt(count_ne.metric_count_nm), 50.79, places=1)

        # 2B: Denier (D) System
        count_den = frappe.get_doc({
            "doctype": "Yarn Count Master",
            "count_code": "UT_150D",
            "count_name": "Unit Test 150 Denier",
            "count_system": "Denier (D)",
            "nominal_value": 150.0
        })
        count_den.insert(ignore_permissions=True)
        self.assertEqual(flt(count_den.denier), 150.0)
        self.assertAlmostEqual(flt(count_den.english_cotton_count_ne), 35.43, places=1)
        self.assertAlmostEqual(flt(count_den.tex), 16.67, places=1)

        # 2C: Boundary test: Reject non-positive count values
        count_invalid = frappe.get_doc({
            "doctype": "Yarn Count Master",
            "count_code": "UT_INVALID_COUNT",
            "count_name": "Invalid Zero Count",
            "count_system": "English Cotton Count (Ne)",
            "nominal_value": 0.0
        })
        self.assertRaises(frappe.ValidationError, count_invalid.insert)

    def test_03_unit_yarn_blend_percentage_enforcement(self):
        """Unit Test: Verify mass balance law (sum of component fibres strictly == 100%)."""
        # 3A: Valid 100% blend must succeed
        valid_blend = frappe.get_doc({
            "doctype": "Yarn Blend Master",
            "blend_code": "UT_BLEND_100",
            "blend_name": "Unit Test 60/40 Cotton-Poly",
            "components": [
                {"fibre_type": "COT", "percentage": 60.0},
                {"fibre_type": "POLY", "percentage": 40.0}
            ]
        })
        valid_blend.insert(ignore_permissions=True)
        self.assertTrue(frappe.db.exists("Yarn Blend Master", "UT_BLEND_100"))

        # 3B: Deficient blend (60% + 35% = 95%) must throw ValidationError
        invalid_blend = frappe.get_doc({
            "doctype": "Yarn Blend Master",
            "blend_code": "UT_BLEND_95",
            "blend_name": "Deficient 95% Blend",
            "components": [
                {"fibre_type": "COT", "percentage": 60.0},
                {"fibre_type": "POLY", "percentage": 35.0}
            ]
        })
        self.assertRaises(frappe.ValidationError, invalid_blend.insert)

    def test_04_unit_fabric_type_relaxation_boundary(self):
        """Unit Test: Verify minimum fabric relaxation hours compliance gate (>= 12h)."""
        fbt_invalid = frappe.get_doc({
            "doctype": "Fabric Type",
            "fabric_type_code": "UT_INVALID_FT",
            "fabric_type_name": "Invalid 6h Relaxation",
            "category": "Knit",
            "default_relaxation_hours": 6.0
        })
        self.assertRaises(frappe.ValidationError, fbt_invalid.insert)

    def test_05_unit_shade_master_pantone_syntax(self):
        """Unit Test: Verify regex enforcement of Pantone TCX/TPX syntax format."""
        # 5A: Valid Pantone TCX syntax
        shade_valid = frappe.get_doc({
            "doctype": "Shade Master",
            "shade_code": "UT_SHADE_OK",
            "shade_name": "Valid Navy",
            "pantone_code": "19-4010 TCX",
            "hex_color": "#0A1172"
        })
        shade_valid.insert(ignore_permissions=True)
        self.assertTrue(frappe.db.exists("Shade Master", "UT_SHADE_OK"))

        # 5B: Invalid Pantone syntax
        shade_invalid = frappe.get_doc({
            "doctype": "Shade Master",
            "shade_code": "UT_SHADE_FAIL",
            "shade_name": "Invalid Code",
            "pantone_code": "NAVY-BLUE-XYZ"
        })
        self.assertRaises(frappe.ValidationError, shade_invalid.insert)

    def test_06_unit_shift_master_hours_calculation(self):
        """Unit Test: Verify working hours calculation deducting break duration."""
        shift = frappe.get_doc({
            "doctype": "Shift Master",
            "shift_code": "UT_SHIFT_8H",
            "shift_name": "Unit Test 8h Shift",
            "start_time": "08:00:00",
            "end_time": "16:30:00",
            "break_duration_minutes": 30
        })
        shift.insert(ignore_permissions=True)
        # 8.5 hours total - 0.5 hours break = 8.0 working hours
        self.assertEqual(flt(shift.working_hours), 8.0)

    # =========================================================================
    # TIER 2: INTEGRATION TESTS (Multi-DocType Interactions & Script Reports)
    # =========================================================================

    def test_07_integration_fabric_construction_woven_theoretical_gsm(self):
        """Integration Test: Verify Fabric Construction integrates Yarn Counts to calculate Theoretical GSM."""
        # EPI = 108, PPI = 56, Warp Ne = 20, Weft Ne = 20
        # Formula: GSM = (108/20 + 56/20) * 25.6 = 8.2 * 25.6 = 209.92
        fc = frappe.get_doc({
            "doctype": "Fabric Construction",
            "construction_code": "INT_TWILL_CALC",
            "construction_name": "Integration Test Twill",
            "fabric_type": "TWILL",
            "structure_type": "Woven",
            "warp_count": "20S_NE",
            "weft_count": "20S_NE",
            "epi": 108.0,
            "ppi": 56.0
        })
        fc.insert(ignore_permissions=True)
        self.assertAlmostEqual(flt(fc.theoretical_gsm), 209.92, places=1)

    def test_08_integration_yarn_count_converter_matrix_report(self):
        """Integration Test: Execute Yarn Count Converter Matrix Script Report and verify live data generation."""
        from ob_apparel.textile_setup_and_masters.report.yarn_count_converter_matrix.yarn_count_converter_matrix import execute
        columns, data = execute()
        self.assertTrue(len(columns) >= 7)
        self.assertTrue(len(data) >= 1)
        # Verify first row has required fields
        first_row = data[0]
        self.assertIn("english_cotton_count_ne", first_row)
        self.assertIn("denier", first_row)
        self.assertIn("tex", first_row)

    # =========================================================================
    # TIER 3: END-TO-END (E2E) TESTS (Complete Business Lifecycle Simulation)
    # =========================================================================

    def test_09_e2e_textile_master_setup_to_readiness_audit(self):
        """E2E Test: Validate that all 12 masters integrate to achieve 100% System Readiness Score in Audit Report."""
        from ob_apparel.textile_setup_and_masters.report.textile_setup_readiness_audit.textile_setup_readiness_audit import execute
        columns, data, chart, msg, summary = execute()
        
        # Verify summary contains 100.0% readiness
        readiness_entry = next((s for s in summary if s.get("label") == "System Setup Readiness"), None)
        self.assertIsNotNone(readiness_entry)
        self.assertEqual(readiness_entry.get("value"), "100.0%")
        self.assertEqual(readiness_entry.get("indicator"), "Green")

        # Verify all 12 rows are 'Ready'
        for row in data:
            self.assertEqual(row.get("status"), "Ready", f"DocType {row.get('doctype_name')} is not Ready!")

    # =========================================================================
    # ARCHITECTURAL DISCIPLINE: ZERO-CORE TOUCH INTEGRITY
    # =========================================================================

    def test_10_gravitas_zero_core_integrity(self):
        """Discipline Test: Assert ZERO modified files exist in apps/frappe or apps/erpnext."""
        for core_app in ["frappe", "erpnext"]:
            app_dir = f"/home/pavithran/frappe-bench/apps/{core_app}"
            res = subprocess.run(["git", "status", "--porcelain"], cwd=app_dir, capture_output=True, text=True)
            self.assertEqual(res.stdout.strip(), "", f"Core app {core_app} has modified files! Zero-core discipline violated.")
