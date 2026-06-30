"""Extracts authority record data from MARC records of LCGFT, CYAC, LCSH (including subdivisions), LCDGT, and LCMPT"""
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
typecounter = {
    "sh": 0,
    "fd": 0,
    "gd": 0,
    "dg": 0,
    "gf": 0,
    "sj": 0,
    "mp": 0
}

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
    """ creates text string of subfields; checks for keyword match if defined, returning True """
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
    """pulls out fields for keyword terms and scope note and institution code, related document field and project notes; if keyword is defined, it limits results"""
    header = ""
    note = ""
    org = ""
    list = ""
    doc = ""
    found = False
    if keyword is None:
        found = True
    headers = record.get_fields("100", "110", "111", "130", "150", "151", "155", "162", "180", "185")
    found, header = fetch_fieldinfo(found, headers, keyword)
    ufs = record.get_fields("400", "410", "411", "430", "450", "451", "455", "462", "480", "485")
    found, uf = fetch_fieldinfo(found, ufs, keyword)
    bts = record.get_fields("500", "510", "511", "530", "550", "551", "555", "562", "580", "585")
    found, bt = fetch_fieldinfo(found, bts, keyword)
    orgs = record.get_fields("040")
    found, org = fetch_fieldinfo(found, orgs, keyword)
    docs = record.get_fields("072")
    found, doc = fetch_fieldinfo(found, docs, keyword)
    lists = record.get_fields("906")
    found, list = fetch_fieldinfo(found, lists, keyword)
    notes = record.get_fields("680")
    found, note = fetch_fieldinfo(found, notes, keyword)
    if found:
        line = [lccn, header, uf, bt, note, org, list, doc]
        return(line)
    else:
        return(None)


def processrecord(filename, type, keyword):
    """processes records in file based on type, whch is [sh | fd | gd | dg | gf | sj | mp] """
    global reccounter
    global typecounter
    marc_gen = reading_marc(filename)
    for record in marc_gen:
        reccounter = reccounter + 1
        result = None
        lccn = lccnno(record)
        if lccn != "":
            typecounter[lccn[0:2]] += 1
        prefix = type
        if type == "fd" or type == "gd":
            prefix = "sh"
        try:
            if lccn.startswith(prefix):
                if type == "fd" and record.get_fields("185") and record.get_fields("185")[0].get_subfields("v"):
                    typecounter["fd"] += 1
                    # fd typecount will only show when fd is type selected
                    typecounter["sh"] += -1
                    result = fetch_results(lccn, record, keyword)
                elif type == "gd" and record.get_fields("180") and record.get_fields("180")[0].get_subfields("x"):
                    typecounter["gd"] += 1
                    # gd typecount will only show when gd is type selected
                    typecounter["sh"] += -1
                    result = fetch_results(lccn, record, keyword)
                elif type == "sh":
                    result = fetch_results(lccn, record, keyword)
                elif type == "sj":
                    result = fetch_results(lccn, record, keyword)
                elif type == "dg":
                    if record.get_fields("150") and record.get_fields("150")[0].get_subfields("a"):
                        result = fetch_results(lccn, record, keyword)
                elif type == "mp" and record.get_fields("162") and record.get_fields("162")[0].get_subfields("a"):
                    result = fetch_results(lccn, record, keyword)
                elif type == "gf" and record.get_fields("155") and record.get_fields("155")[0].get_subfields("a"):
                    result = fetch_results(lccn, record, keyword)
        except KeyError:
            print(KeyError)
            pass
        if result is not None and result[1] is not None:
            yield(result)


def processfile(filename, type, csvfile, keyword):
    """looks at each record according to type to extract data to a csv file"""
    global hitcounter
    try:
        with open(csvfile, "w", newline='', encoding='utf-8') as myfile:
            wr = csv.writer(myfile)
            wr.writerow(["LCCN", "Heading", "Variants", "Broader Terms", "Notes", "Organizations", "Monthly list", "SHM docs"])
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
    parser.add_argument("-o", help="Path to csv file output required.", required=True, metavar="output")
    parser.add_argument("-key", help="If more than one keyword, enclose in quotes.")
    args = parser.parse_args()
    
    keyword = None
    keytext = "[No keyword given]"    
    filename = args.filename
    type = args.type
    csvfile = args.o
    if not filename.endswith(".mrc"):
        sys.exit(f"{filename} not a valid path; must end in .mrc")
    if not os.path.exists(filename):
        sys.exit(f"{filename} not found")
    if args.key:
        keyword = args.key
        keytext = keyword
    #update to tell them what we are about to do
    print(f"{filename} {type} {csvfile} {keytext}")
    if keyword is not None:
        keyword = keyword.strip()
        keyword = unicodedata.normalize("NFC", keyword)
    processfile(filename, type, csvfile, keyword)
    for key in typecounter.keys():
        print(f"{key}: {typecounter[key]}")
    print(f"{reccounter} read, {hitcounter} found")

'''
Expected output is: csv file containing LCCN (identifier), 1XX (subject heading), all 4XX (cross-references), 5XX (broader and related terms), 680 (scope note), orgs (040), list (906), docs (072).
'''

