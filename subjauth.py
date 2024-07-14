"""Extracts genre/form data from LCGFT and LCSH"""
import sys
import os
import argparse
import csv
import unicodedata
from pymarc import MARCReader
from pymarc.exceptions import PymarcException

HELP = "python subjauth.py <input file path> -type [sh | fd | gd | dg | gf | sj | mp] -o <csv path> [-key <keyword string>]"
reccounter = 0
hitcounter = 0

def reading_marc(filename):
    """Reads the whole MARC file"""
    try:
        with open(filename, 'rb') as fh:
            reader = MARCReader(fh, to_unicode=True, force_utf8=True)
            for record in reader:
                if record is None:
                    sys.exit("Problem with MARC file. Record is 'None'.")
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
  try:
      lccn = record['010']['a'].strip()
  except Exception:
      print(f"lccno not found in recno {reccounter}")
      lccn = ""
  return (lccn)

def analyze_subfields(field, infound, keyword):
    textstring = ""
    found = infound
    subfields = field.subfields
    for subfield in subfields:
        key = subfield[0]
        value = subfield[1]
        if keyword is not None and not found:
            words = value.split() 
            for word in words:
                if word.startswith(keyword):
                    found = True
                    break
        textstring = textstring + "$" + key + " " + value + " "
    textstring = textstring.strip()
    textstring = unicodedata.normalize("NFC", textstring)
    return([found, textstring])

def fetch_fieldinfo(found, list, keyword):
    """find data in MARC fields"""
    value = ""
    returnval = ""
    for field in list:
        if field is not None:
            found,value = analyze_subfields(field, found, keyword)
            returnval= returnval + value + " | " 
    return([found, returnval])

def fetch_results(lccn, record, keyword):
    """pulls out fields for keyword terms and scope note"""
    header = ""
    note = ""
    found = False
    if keyword is None:
        found = True
    headers = record.get_fields("100", "110", "111", "130", "150", "151", "155", "162", "185")
    found, header = fetch_fieldinfo(found, headers, keyword)
    #print(header)
    ufs = record.get_fields("400", "410", "411", "430", "450", "451", "455", "462", "485")
    found, uf = fetch_fieldinfo(found, ufs, keyword)
    #print(uf)
    bts = record.get_fields("500", "510", "511", "530", "550", "551", "555", "562", "585")
    found, bt = fetch_fieldinfo(found, bts, keyword)
    #print(bt)
    notes = record.get_fields("680")
    found, note = fetch_fieldinfo(found, notes, keyword)
    if found:
        return([lccn, header, uf, bt, note])
    else:
        return(None)


def processrecord(filename, type, keyword):
    """processes records in file based on type, whch is [sh | fd | gd | dg | gf | sj | mp] """
    global reccounter
    marc_gen = reading_marc(filename)
    for record in marc_gen:
        reccounter = reccounter + 1
        result = None
        lccn = lccnno(record)
        prefix = type
        if type == "fd" or "gd":
            prefix == "sh"
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
    global hitcounter
    try:
        with open(csvfile, "w", newline='', encoding='utf-8') as myfile:
            wr = csv.writer(myfile)
            for line in processrecord(filename, type, keyword):
                hitcounter = hitcounter + 1
                try:
                    if line is not None:
                        wr.writerow(line)
                except Exception as e:
                    sys.exit(f"Problem writing line '{line}' {e.__class__.__doc__} ")
    except Exception as e:
        sys.exit(f"Problem found in writing to {csvfile}: {e.__class__.__doc__} [{e.__class__.__name__}]")

if __name__ == "__main__":
    # command line arguments
    parser = argparse.ArgumentParser(description='Get options.')
    parser.add_argument("filename", help="Path to marc file required.")
    parser.add_argument("-type", choices=["sh", "fd", "gd", "dg", "gf", "sj", "mp"], required=True)
    parser.add_argument("-key", help="If more than one keyword, enclose in quotes.")
    parser.add_argument("-o", help="Path to csv file output required.", required=True, metavar="output")
    args = parser.parse_args()
    #print("we parsed")
    
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
    print(f"{filename} {type} {csvfile} {keyword}")
#update to tell them what we are about to do; also ReadMe file for help 2024-02-09
    if keyword is not None:
        keyword = keyword.strip()
        keyword = unicodedata.normalize("NFC", keyword)
    processfile(filename, type, csvfile, keyword)
    print(f"{reccounter} read, {hitcounter} found")

'''
figure out why filename isn't recognized as an argument 2024-02-23
Expected output is: csv file containing LCCN (identifier), 1XX (subject heading), all 4XX (cross-references), 5XX (broader and related terms), 680 (scope note).
'''

