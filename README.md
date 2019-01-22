VCF2CSV
=======

VCF2CSV is a simple Vcard to CSV converter.

Presently, it only understands the Name, Full Name, and Email fields.

Usage:

```
usage: vcf2csv.py [-h] [--ignore_no_email] input_file output_file

Convert VCF file to CSV.

positional arguments:
  input_file         vcf file to process
  output_file        csv file to output

optional arguments:
  -h, --help         show this help message and exit
  --ignore_no_email  ignore entries with no email
```
