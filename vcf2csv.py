import argparse
import csv
import re
import sys
import time

# VCF regex matches
RE_VCF_BEGIN = r'^BEGIN:VCARD$'
RE_VCF_END = r'^END:VCARD$'
RE_VCF_NAME = r'^N:(.+);(.+);(.*);(.*);$'
RE_VCF_FULL_NAME = r'^FN:(.*)$'
RE_VCF_EMAIL= r'.*EMAIL.*type=INTERNET.*:(.*)$'

FIELD_NAMES = ['name', 'full_name', 'email', 'email2']

def parse_vcf(vcf_file, ignore_no_email):
    data = []
    line_data = {}
    for line in vcf_file:
        line = line.strip()
        # Handle lines that are beginnings and ends of cards
        if re.match(RE_VCF_BEGIN, line):
            line_data = {}
        if re.match(RE_VCF_END, line):
            if line_data != {}:
                for field in FIELD_NAMES:
                    if field not in line_data:
                        line_data[field] = ""

                if ignore_no_email and line_data['email'] == "":
                    continue
                data = data + [line_data]
                continue

        name = re.match(RE_VCF_NAME, line)
        full_name = re.match(RE_VCF_FULL_NAME, line)
        email = re.match(RE_VCF_EMAIL, line)

        if name:
            line_data['name'] = ("%s %s" % (name.group(2), name.group(1))).strip()
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
    with open(input_file, 'r') as vcf_file:
        data = parse_vcf(vcf_file, ignore_no_email)

    with open(output_file, 'w') as csv_file:
        write_csv(data, csv_file)

    return 0

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Convert VCF file to CSV.')
    parser.add_argument('input_file', type=str, help='vcf file to process')
    parser.add_argument('output_file', type=str, help='csv file to output')
    parser.add_argument('--ignore_no_email', action='store_true',
        help='ignore entries with no email')
    args = parser.parse_args()

    sys.exit(main(args.input_file, args.output_file, args.ignore_no_email))
