import argparse
import csv
import re
import sys

# VCF regex matches - compiled with case-insensitive flag
RE_VCF_BEGIN = re.compile(r'^BEGIN:VCARD$', re.IGNORECASE)
RE_VCF_END = re.compile(r'^END:VCARD$', re.IGNORECASE)
RE_VCF_NAME = re.compile(r'^N:([^;]*);([^;]*);?([^;]*);?([^;]*);?([^;]*)?$', re.IGNORECASE)
RE_VCF_FULL_NAME = re.compile(r'^FN:(.*)$', re.IGNORECASE)
RE_VCF_EMAIL = re.compile(r'^EMAIL[^:]*:(.+)$', re.IGNORECASE)

FIELD_NAMES = ['first_name', 'last_name', 'full_name', 'email', 'email2']

def parse_vcf(vcf_file, ignore_no_email):
    data = []
    line_data = {}
    for line in vcf_file:
        line = line.strip()
        # Handle lines that are beginnings and ends of cards
        if RE_VCF_BEGIN.match(line):
            line_data = {}
        if RE_VCF_END.match(line):
            if line_data != {}:
                for field in FIELD_NAMES:
                    if field not in line_data:
                        line_data[field] = ""

                if ignore_no_email and line_data['email'] == "":
                    continue
                data = data + [line_data]
                continue

        name = RE_VCF_NAME.match(line)
        full_name = RE_VCF_FULL_NAME.match(line)
        email = RE_VCF_EMAIL.match(line)

        if name:
            line_data['first_name'] = name.group(2).strip()
            line_data['last_name'] = name.group(1).strip()
        if full_name:
            line_data['full_name'] = full_name.group(1).strip()
        if email:
            if "email" not in line_data:
                line_data['email'] = email.group(1).strip()
            else:
                line_data['email2'] = email.group(1).strip()

    return data


def write_csv(data, csv_file):
    writer = csv.DictWriter(csv_file, fieldnames=FIELD_NAMES)
    writer.writeheader()
    for line in data:
        writer.writerow(line)

def main(input_file, output_file, ignore_no_email):
    try:
        with open(input_file, 'r', encoding='utf-8') as vcf_file:
            data = parse_vcf(vcf_file, ignore_no_email)

        with open(output_file, 'w', encoding='utf-8', newline='') as csv_file:
            write_csv(data, csv_file)
    except FileNotFoundError as e:
        print(f"Error: File not found - {e.filename}", file=sys.stderr)
        return 1
    except PermissionError as e:
        print(f"Error: Permission denied - {e.filename}", file=sys.stderr)
        return 1
    except IOError as e:
        print(f"Error: I/O error occurred - {e}", file=sys.stderr)
        return 1

    return 0

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Convert VCF file to CSV.')
    parser.add_argument('input_file', type=str, help='vcf file to process')
    parser.add_argument('output_file', type=str, help='csv file to output')
    parser.add_argument('--ignore_no_email', action='store_true',
        help='ignore entries with no email')
    args = parser.parse_args()

    sys.exit(main(args.input_file, args.output_file, args.ignore_no_email))
