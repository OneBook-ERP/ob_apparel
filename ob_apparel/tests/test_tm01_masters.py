import subprocess
import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import flt

class TestTM01Masters(FrappeTestCase):
    def setUp(self):
        frappe.set_user("Administrator")

    def test_01_textile_settings_boundary_validation(self):
        settings = frappe.get_doc("Textile Settings")
        
        # Test 1: Minimum Relaxation Hours < 12h must fail
        settings.min_relaxation_hours = 8.0
        self.assertRaises(frappe.ValidationError, settings.save)

        # Test 2: Weight Tolerance > 5% must fail
        settings.reload()
        settings.weight_tolerance_percentage = 8.0
        self.assertRaises(frappe.ValidationError, settings.save)

        # Test 3: Grade A >= Grade B must fail
        settings.reload()
        settings.grade_a_max_points = 45.0
        settings.grade_b_max_points = 40.0
        self.assertRaises(frappe.ValidationError, settings.save)

    def test_02_yarn_count_conversions(self):
        # Test Ne system
        count_ne = frappe.get_doc({
            "doctype": "Yarn Count Master",
            "count_code": "TEST_30S_NE",
            "count_name": "Test 30s Ne",
            "count_system": "English Cotton Count (Ne)",
            "nominal_value": 30.0
        })
        count_ne.insert(ignore_permissions=True)
        self.assertEqual(flt(count_ne.english_cotton_count_ne), 30.0)
        self.assertAlmostEqual(flt(count_ne.denier), 177.17, places=1)
        self.assertAlmostEqual(flt(count_ne.tex), 19.68, places=1)
        self.assertAlmostEqual(flt(count_ne.metric_count_nm), 50.79, places=1)

        # Test Denier system
        count_den = frappe.get_doc({
            "doctype": "Yarn Count Master",
            "count_code": "TEST_150D",
            "count_name": "Test 150 Denier",
            "count_system": "Denier (D)",
            "nominal_value": 150.0
        })
        count_den.insert(ignore_permissions=True)
        self.assertEqual(flt(count_den.denier), 150.0)
        self.assertAlmostEqual(flt(count_den.english_cotton_count_ne), 35.43, places=1)
        self.assertAlmostEqual(flt(count_den.tex), 16.67, places=1)

        # Test zero/negative count failure
        count_invalid = frappe.get_doc({
            "doctype": "Yarn Count Master",
            "count_code": "TEST_INVALID_COUNT",
            "count_name": "Invalid Zero Count",
            "count_system": "English Cotton Count (Ne)",
            "nominal_value": 0.0
        })
        self.assertRaises(frappe.ValidationError, count_invalid.insert)

    def test_03_yarn_blend_percentage_enforcement(self):
        # Valid 100% blend must succeed
        valid_blend = frappe.get_doc({
            "doctype": "Yarn Blend Master",
            "blend_code": "TEST_BLEND_100",
            "blend_name": "Test Valid Blend 60/40",
            "components": [
                {"fibre_type": "COT", "percentage": 60.0},
                {"fibre_type": "POLY", "percentage": 40.0}
            ]
        })
        valid_blend.insert(ignore_permissions=True)
        self.assertTrue(frappe.db.exists("Yarn Blend Master", "TEST_BLEND_100"))

        # Invalid 95% blend must fail
        invalid_blend = frappe.get_doc({
            "doctype": "Yarn Blend Master",
            "blend_code": "TEST_BLEND_FAIL",
            "blend_name": "Test Invalid Blend 60/35",
            "components": [
                {"fibre_type": "COT", "percentage": 60.0},
                {"fibre_type": "POLY", "percentage": 35.0}
            ]
        })
        self.assertRaises(frappe.ValidationError, invalid_blend.insert)

    def test_04_fabric_type_relaxation_boundary(self):
        # Default relaxation < 12h must fail
        fbt_invalid = frappe.get_doc({
            "doctype": "Fabric Type",
            "fabric_type_code": "TEST_INVALID_FT",
            "fabric_type_name": "Invalid Quick Dry",
            "category": "Knit",
            "default_relaxation_hours": 6.0
        })
        self.assertRaises(frappe.ValidationError, fbt_invalid.insert)

    def test_05_fabric_construction_theoretical_gsm(self):
        # Woven theoretical GSM calculation
        # EPI = 108, PPI = 56, Warp Ne = 20, Weft Ne = 20
        # GSM = (108/20 + 56/20) * 25.6 = 8.2 * 25.6 = 209.92
        fc = frappe.get_doc({
            "doctype": "Fabric Construction",
            "construction_code": "TEST_TWILL_CALC",
            "construction_name": "Test Twill Calc",
            "fabric_type": "TWILL",
            "structure_type": "Woven",
            "warp_count": "20S_NE",
            "weft_count": "20S_NE",
            "epi": 108.0,
            "ppi": 56.0
        })
        fc.insert(ignore_permissions=True)
        self.assertAlmostEqual(flt(fc.theoretical_gsm), 209.92, places=1)

    def test_06_shade_master_pantone_syntax(self):
        # Valid Pantone TCX syntax
        shade_valid = frappe.get_doc({
            "doctype": "Shade Master",
            "shade_code": "TEST_SHADE_OK",
            "shade_name": "Test Valid Navy",
            "pantone_code": "19-4010 TCX",
            "hex_color": "#0A1172"
        })
        shade_valid.insert(ignore_permissions=True)
        self.assertTrue(frappe.db.exists("Shade Master", "TEST_SHADE_OK"))

        # Invalid Pantone syntax
        shade_invalid = frappe.get_doc({
            "doctype": "Shade Master",
            "shade_code": "TEST_SHADE_FAIL",
            "shade_name": "Test Invalid Shade",
            "pantone_code": "NAVY-BLUE-XYZ"
        })
        self.assertRaises(frappe.ValidationError, shade_invalid.insert)

    def test_07_shift_master_hours_calculation(self):
        shift = frappe.get_doc({
            "doctype": "Shift Master",
            "shift_code": "TEST_SHIFT_CALC",
            "shift_name": "Test Shift 8h",
            "start_time": "08:00:00",
            "end_time": "16:30:00",
            "break_duration_minutes": 30
        })
        shift.insert(ignore_permissions=True)
        # 8.5 hours - 0.5 break = 8.0 hours
        self.assertEqual(flt(shift.working_hours), 8.0)

    def test_08_gravitas_zero_core_integrity(self):
        # Verify apps/frappe and apps/erpnext are clean
        for core_app in ["frappe", "erpnext"]:
            app_dir = f"/home/pavithran/frappe-bench/apps/{core_app}"
            res = subprocess.run(["git", "status", "--porcelain"], cwd=app_dir, capture_output=True, text=True)
            self.assertEqual(res.stdout.strip(), "", f"Core app {core_app} has modified files! Zero-core discipline violated.")
