"""Extracts genre/form data from LCGFT and LCSH"""
import sys
import os
import argparse
import csv
import unicodedata
from pymarc import MARCReader
from pymarc.exceptions import PymarcException

HELP = "python subjauth.py <input file path> -type [sh | fd | gd | dg | gf | sj | mp] -o <csv path> [-key <keyword string>]"

def reading_marc(filename):
    """Reads the whole MARC file"""
    try:
        with open(filename, 'rb') as fh:
            reader = MARCReader(fh, to_unicode=True, force_utf8=True)
            for record in reader:
                yield record
    except FileNotFoundError:
        sys.exit(f"MARC file {filename} not found")
    except OSError as e:
        sys.exit(f"Problem with MARC file: {e.__class__.__doc__} [{e.__class__.__name__}]")
    except PymarcException as e:
        sys.exit(f"Problem reading MARC file: {e.__class__.__doc__} [{e.__class__.__name__}]")
    except Exception as e:
        sys.exit(f"Problem found: {e.__class__.__doc__} [{e.__class__.__name__}]")

def lccnno(record):
  """pulls out 010 $a from the fields collection as an identifier"""
  lccn = record['010']['a'].strip()
  return (lccn)

def analyze_subfields(field, infound, keyword):
    textstring = ""
    found = infound
    subfields = field.subfields
    keys = subfields[::2]
    values = subfields[1::2]
    for i in range(0, len(keys)):
        if not found:
            words = values[i].split()
            for word in words:
                if word.startswith(keyword):
                    found = True
                    break
        textstring = textstring + "$" + keys[i] + " " + values[i] + " "
    textstring = textstring.strip()
    textstring = unicodedata.normalize("NFC", textstring)
    return([found, textstring])


def fetch_results(lccn, record, keyword):
    """pulls out fields for keyword terms and scope note"""
    header = ""
    note = ""
    if keyword == "":
        found = True
    for num in ["100", "110", "111", "130", "150", "151", "155", "162", "185"]:
        if record[num] is not None:
            found, header = analyze_subfields(record[num], found, keyword)
            break
    print(header)
    uf = ""
    for num in ["400", "410", "411", "430", "450", "451", "455", "462", "485"]:
        if record[num] is not None:
            found, uft = analyze_subfields(record[num], found, keyword)
            uf = uf + uft + " | " 
    print(uf)
    bt = ""
    for num in ["500", "510", "511", "530", "550", "551", "555", "562", "585"]:
        if record[num] is not None:
            found, btt = analyze_subfields(record[num], found, keyword)
            bt = bt + btt + " | " 
    print(bt)
    if record["680"] is not None and record["680"]["i"] is not None:
        found, note = analyze_subfields(record["680"], found, keyword)
    if found:
        return([lccn, header, uf, bt, note])
    else:
        return(None)


def processrecord(filename, type, keyword):
    """processes records in file based on type, whch is [sh | fd | gd | dg | gf | sj | mp] """
    marc_gen = reading_marc(filename)
    for record in marc_gen:
        result = None
        lccn = lccnno(record)
        prefix = type
        if type == "fd":
            prefix = "sh"
        if lccn.startswith(prefix):
            if type == "fd" and record["185"] is not None and record["185"]["v"] is not None:
                result = fetch_results(lccn, record, keyword)
            if type == "gd" and record["185"] is not None and record["185"]["x"] is not None:
                result = fetch_results(lccn, record, keyword)
            elif type == "sh":
                result = fetch_results(lccn, record, keyword)
            elif type == "sj":
                result = fetch_results(lccn, record, keyword)
            elif type == "dg" and record["150"] is not None and record["150"]["a"] is not None:
                result = fetch_results(lccn, record, keyword)
            elif type == "mp" and record["162"] is not None and record["162"]["a"] is not None:
                result = fetch_results(lccn, record, keyword)
            elif type == "gf" and record["155"] is not None and record["155"]["a"] is not None:
                result = fetch_results(lccn, record, keyword)
            if result is not None and result[1] is not None:
                yield(result)


def processfile(filename, type, csvfile, keyword):
    """looks at each record according to type to extract data to a csv file"""
    try:
        with open(csvfile, "w", newline='', encoding='utf-8') as myfile:
            wr = csv.writer(myfile)
            for line in processrecord(filename, type, keyword):
                if line is not None:
                    wr.writerow(line)
    except Exception as e:
        sys.exit(f"Problem found in writing to {filename}: {e.__class__.__doc__} [{e.__class__.__name__}]")

if __name__ == "__main__":
    # command line arguments
    parser = argparse.ArgumentParser(description='Get options.')
    parser.add_argument("filename", help="Path to marc file required.")
    parser.add_argument("-type", choices=["sh", "fd", "gd", "dg", "gf", "sj", "mp"], required=True)
    parser.add_argument("-key", help="If more than one keyword, enclose in quotes.")
    parser.add_argument("-o", help="Path to csv file output required.", required=True)
    args = parser.parse_args(sys.argv)
    
    keyword = None    
    filename = args.filename
    type = args.type
    csvfile = args.o
    if not filename.endswith(".mrc"):
        sys.exit(f"{filename} not a valid path; must end in .mrc")
    if not os.path.exists(filename):
        sys.exit(f"{filename} not found")
    if args.key:
        keyword = args.key 
#update to tell them what we are about to do; also ReadMe file for help 2024-02-09

    processfile(filename, type, csvfile, keyword)

'''
figure out why filename isn't recognized as an argument 2024-02-23
Expected output is: csv file containing LCCN (identifier), 1XX (subject heading), all 4XX (cross-references), 5XX (broader and related terms), 680 (scope note).
'''

