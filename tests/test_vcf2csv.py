#!/usr/bin/env python
"""Test suite for vcf2csv.py"""

import csv
import os
import sys
import tempfile
import unittest

# Add parent directory to path to import vcf2csv
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import vcf2csv


class TestVCF2CSV(unittest.TestCase):
    """Test cases for VCF to CSV conversion"""

    def setUp(self):
        """Set up test fixtures directory"""
        self.fixtures_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        shutil.rmtree(self.temp_dir)

    def get_fixture_path(self, filename):
        """Get full path to a fixture file"""
        return os.path.join(self.fixtures_dir, filename)

    def get_temp_output_path(self, filename='output.csv'):
        """Get path for temporary output file"""
        return os.path.join(self.temp_dir, filename)

    def read_csv_output(self, csv_path):
        """Read CSV file and return list of dicts"""
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)

    def test_example1_single_contact(self):
        """Test parsing example1.vcf - single contact from GitHub example"""
        input_file = self.get_fixture_path('example1.vcf')
        output_file = self.get_temp_output_path()

        result = vcf2csv.main(input_file, output_file, ignore_no_email=False)
        self.assertEqual(result, 0, "Conversion should succeed")

        data = self.read_csv_output(output_file)
        self.assertEqual(len(data), 1, "Should have 1 contact")

        contact = data[0]
        self.assertEqual(contact['first_name'], 'John')
        self.assertEqual(contact['last_name'], 'Doe')
        self.assertEqual(contact['full_name'], 'John Doe')
        self.assertEqual(contact['email'], 'forrestgump@example.com')
        self.assertEqual(contact['email2'], 'example@example.com')
        self.assertEqual(contact['phone'], '(111) 555-1212')
        self.assertEqual(contact['phone2'], '(404) 555-1212')

    def test_example2_multiple_contacts(self):
        """Test parsing example2.vcf - multiple contacts from RFC 6350"""
        input_file = self.get_fixture_path('example2.vcf')
        output_file = self.get_temp_output_path()

        result = vcf2csv.main(input_file, output_file, ignore_no_email=False)
        self.assertEqual(result, 0, "Conversion should succeed")

        data = self.read_csv_output(output_file)
        self.assertEqual(len(data), 2, "Should have 2 contacts")

        # Check first contact
        self.assertEqual(data[0]['first_name'], 'Jane')
        self.assertEqual(data[0]['last_name'], 'Doe')
        self.assertEqual(data[0]['email'], 'jane.doe@abc.com')

        # Check second contact
        self.assertEqual(data[1]['first_name'], 'Bob')
        self.assertEqual(data[1]['last_name'], 'Smith')
        self.assertEqual(data[1]['email'], 'bob.smith@company.com')
        self.assertEqual(data[1]['email2'], 'bob@personal.com')

    def test_edge_cases_case_insensitive(self):
        """Test edge_cases.vcf - case insensitivity and special characters"""
        input_file = self.get_fixture_path('edge_cases.vcf')
        output_file = self.get_temp_output_path()

        result = vcf2csv.main(input_file, output_file, ignore_no_email=False)
        self.assertEqual(result, 0, "Conversion should succeed")

        data = self.read_csv_output(output_file)
        self.assertEqual(len(data), 6, "Should have 6 contacts")

        # Test case insensitive matching (lowercase begin:vcard and n:)
        jane = data[1]
        self.assertEqual(jane['first_name'], 'Jane')
        self.assertEqual(jane['last_name'], 'Smith')
        self.assertEqual(jane['email'], 'jane@example.com')

        # Test international characters (UTF-8)
        jose = data[2]
        self.assertEqual(jose['first_name'], 'José')
        self.assertEqual(jose['last_name'], 'García')

        ming = data[3]
        self.assertEqual(ming['first_name'], '明')
        self.assertEqual(ming['last_name'], '李')

    def test_ignore_no_email_flag(self):
        """Test --ignore_no_email flag filters contacts without email"""
        input_file = self.get_fixture_path('edge_cases.vcf')
        output_file = self.get_temp_output_path()

        result = vcf2csv.main(input_file, output_file, ignore_no_email=True)
        self.assertEqual(result, 0, "Conversion should succeed")

        data = self.read_csv_output(output_file)
        self.assertEqual(len(data), 5, "Should have 5 contacts (1 filtered)")

        # Verify no empty emails
        for contact in data:
            self.assertNotEqual(contact['email'], '',
                              f"Contact {contact['full_name']} should have email")

    def test_name_without_trailing_semicolons(self):
        """Test N: field without trailing semicolons (Bug fix #2)"""
        input_file = self.get_fixture_path('edge_cases.vcf')
        output_file = self.get_temp_output_path()

        result = vcf2csv.main(input_file, output_file, ignore_no_email=False)
        data = self.read_csv_output(output_file)

        # First contact has N:Doe;John (no trailing semicolons)
        john = data[0]
        self.assertEqual(john['first_name'], 'John')
        self.assertEqual(john['last_name'], 'Doe')

    def test_email_variants(self):
        """Test various EMAIL field formats (Bug fix #3)"""
        input_file = self.get_fixture_path('edge_cases.vcf')
        output_file = self.get_temp_output_path()

        result = vcf2csv.main(input_file, output_file, ignore_no_email=False)
        data = self.read_csv_output(output_file)

        # Test EMAIL;TYPE=work:
        self.assertEqual(data[0]['email'], 'john@example.com')

        # Test plain email:
        self.assertEqual(data[1]['email'], 'jane@example.com')

        # Test EMAIL;TYPE=INTERNET:
        self.assertEqual(data[2]['email'], 'jose@example.com')

    def test_file_not_found_error(self):
        """Test error handling for missing input file (Bug fix #5)"""
        output_file = self.get_temp_output_path()

        result = vcf2csv.main('nonexistent.vcf', output_file, ignore_no_email=False)
        self.assertEqual(result, 1, "Should return error code 1")

    def test_utf8_encoding(self):
        """Test UTF-8 encoding handles international characters (Bug fix #6)"""
        input_file = self.get_fixture_path('edge_cases.vcf')
        output_file = self.get_temp_output_path()

        result = vcf2csv.main(input_file, output_file, ignore_no_email=False)
        self.assertEqual(result, 0)

        data = self.read_csv_output(output_file)

        # Verify international characters are preserved
        jose = next(c for c in data if c['last_name'] == 'García')
        self.assertEqual(jose['first_name'], 'José')

        ming = next(c for c in data if c['last_name'] == '李')
        self.assertEqual(ming['first_name'], '明')

    def test_phone_extraction(self):
        """Test phone number extraction with various formats"""
        input_file = self.get_fixture_path('phone_test.vcf')
        output_file = self.get_temp_output_path()

        result = vcf2csv.main(input_file, output_file, ignore_no_email=False)
        self.assertEqual(result, 0, "Conversion should succeed")

        data = self.read_csv_output(output_file)
        self.assertEqual(len(data), 3, "Should have 3 contacts")

        # Test single phone number
        self.assertEqual(data[0]['phone'], '+1-234-567-8900')
        self.assertEqual(data[0]['phone2'], '')

        # Test multiple phone numbers
        self.assertEqual(data[1]['phone'], '555-1234')
        self.assertEqual(data[1]['phone2'], '(555) 555-5678')

        # Test no phone number
        self.assertEqual(data[2]['phone'], '')
        self.assertEqual(data[2]['phone2'], '')


class TestVCFParser(unittest.TestCase):
    """Test the parse_vcf function directly"""

    def test_empty_file(self):
        """Test parsing empty file"""
        from io import StringIO
        vcf_data = StringIO("")
        result = vcf2csv.parse_vcf(vcf_data, ignore_no_email=False)
        self.assertEqual(result, [])

    def test_single_contact(self):
        """Test parsing single contact"""
        from io import StringIO
        vcf_data = StringIO("""BEGIN:VCARD
N:Doe;John
FN:John Doe
EMAIL:john@example.com
END:VCARD
""")
        result = vcf2csv.parse_vcf(vcf_data, ignore_no_email=False)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['first_name'], 'John')
        self.assertEqual(result[0]['last_name'], 'Doe')
        self.assertEqual(result[0]['email'], 'john@example.com')


def run_tests():
    """Run all tests and return exit code"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
