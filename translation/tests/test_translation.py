import unittest
import json
import os
import sys

# Scripts live in translation/scripts/, resources in translation/resources/
SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts")
RESOURCES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources")
sys.path.insert(0, SCRIPTS_DIR)

try:
    from generate_c import CCodeGenerator
    from generate_cpp import CppCodeGenerator
    from generate_java import JavaCodeGenerator
except ImportError as e:
    print(f"[WARN] Could not import generators: {e}")
    CCodeGenerator = None
    CppCodeGenerator = None
    JavaCodeGenerator = None

class TestTranslationPipeline(unittest.TestCase):

    def setUp(self):
        self.type_map_path = os.path.join(RESOURCES_DIR, "type_map.json")
        self.io_map_path = os.path.join(RESOURCES_DIR, "io_map.json")
        self.apm_schema_path = os.path.join(RESOURCES_DIR, "apm_schema.json")

    def test_apm_schema_loads(self):
        """Test that the APM schema is valid JSON."""
        self.assertTrue(os.path.exists(self.apm_schema_path), "apm_schema.json missing")
        with open(self.apm_schema_path, "r") as f:
            schema = json.load(f)
        self.assertIn("properties", schema)
        self.assertIn("required", schema)

    def test_type_map_loads_and_contains_basics(self):
        """Test type mapping structure."""
        self.assertTrue(os.path.exists(self.type_map_path), "type_map.json missing")
        with open(self.type_map_path, "r") as f:
            tmap = json.load(f)
        self.assertIn("canonical_types", tmap)
        self.assertIn("INT", tmap["canonical_types"])
        self.assertEqual(tmap["canonical_types"]["INT"]["java"], "int")
        self.assertEqual(tmap["canonical_types"]["LONG"]["cpp"], "long long")

    def test_io_map_loads(self):
        """Test I/O mappings."""
        self.assertTrue(os.path.exists(self.io_map_path), "io_map.json missing")
        with open(self.io_map_path, "r") as f:
            iomap = json.load(f)
        self.assertIn("io_functions", iomap)
        self.assertIn("string_concat", iomap)

    def test_c_generator_instantiation(self):
        if not CCodeGenerator: self.skipTest("CCodeGenerator could not be imported")
        gen = CCodeGenerator()
        self.assertIsNotNone(gen.type_map)

    def test_java_generator_instantiation(self):
        if not JavaCodeGenerator: self.skipTest("JavaCodeGenerator could not be imported")
        gen = JavaCodeGenerator()
        self.assertIsNotNone(gen.type_map)

    def test_cpp_generator_instantiation(self):
        if not CppCodeGenerator: self.skipTest("CppCodeGenerator could not be imported")
        gen = CppCodeGenerator()
        self.assertIsNotNone(gen.type_map)

    def test_expression_emission(self):
        if not JavaCodeGenerator: self.skipTest("JavaCodeGenerator missing")
        gen = JavaCodeGenerator()
        expr = {"kind": "BINARY_OP", "operator": "+", "left": {"kind": "IDENTIFIER", "name": "a"}, "right": {"kind": "LITERAL", "value": "5"}}
        self.assertEqual(gen.emit_expr(expr), "(a + 5)")

    def test_statement_emission(self):
        if not CCodeGenerator: self.skipTest("CCodeGenerator missing")
        gen = CCodeGenerator()
        stmt = {"kind": "ASSIGN", "target": {"kind": "IDENTIFIER", "name": "x"}, "value": {"kind": "LITERAL", "value": "10"}}
        lines = gen.emit_stmt(stmt, 0)
        self.assertEqual(lines[0], "x = 10;")

    def test_array_size_injection(self):
        if not CCodeGenerator: self.skipTest("CCodeGenerator missing")
        gen = CCodeGenerator()
        expr = {"kind": "MEMBER_ACCESS", "object": {"kind": "IDENTIFIER", "name": "arr"}, "member": "length"}
        self.assertEqual(gen.emit_expr(expr), "n")

    def test_array_size_removal(self):
        if not JavaCodeGenerator: self.skipTest("JavaCodeGenerator missing")
        gen = JavaCodeGenerator()
        expr = {"kind": "MEMBER_ACCESS", "object": {"kind": "IDENTIFIER", "name": "arr"}, "member": "length"}
        self.assertEqual(gen.emit_expr(expr), "arr.length")

    def test_io_mapping_printf_to_println(self):
        if not JavaCodeGenerator: self.skipTest("JavaCodeGenerator missing")
        gen = JavaCodeGenerator()
        stmt = {
            "kind": "PRINT",
            "format": "Sum: %d\\n",
            "arguments": [
                {"kind": "LITERAL", "type": "STRING", "value": "\"Sum: %d\\n\""},
                {"kind": "IDENTIFIER", "name": "total"}
            ]
        }
        lines = gen.emit_stmt(stmt, 1)
        self.assertEqual(lines[0], '    System.out.println("Sum: " + total);')

    def test_io_mapping_println_to_cout(self):
        if not CppCodeGenerator: self.skipTest("CppCodeGenerator missing")
        gen = CppCodeGenerator()
        stmt = {
            "kind": "PRINT",
            "format": "Sum: %d\\n",
            "arguments": [
                {"kind": "LITERAL", "type": "STRING", "value": "\"Sum: %d\\n\""},
                {"kind": "IDENTIFIER", "name": "total"}
            ]
        }
        lines = gen.emit_stmt(stmt, 1)
        self.assertEqual(lines[0], '    std::cout << "Sum: " << total << std::endl;')


if __name__ == "__main__":
    unittest.main()
