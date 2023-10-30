"""Extracts genre/form data from LCGFT and LCSH"""
import sys
import csv
import unicodedata
from pymarc import MARCReader
from pymarc.exceptions import PymarcException

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

def fetch_gf(lccn, record):
    """pulls out headings for genre/form (gf) terms and scope note"""
    header = ""
    note = ""
    subfields = record["155"].subfields
    keys = subfields[::2]
    values = subfields[1::2]
    for i in range(0, len(keys)):
        header = header + "$" + keys[i] + " " + values[i] + " "
    header = header.strip()
    header = unicodedata.normalize("NFC", header)
    print(header)
    if record["680"] is not None and record["680"]["i"] is not None:
        subfields = record["680"].subfields
        keys = subfields[::2]
        values = subfields[1::2]
        for i in range(0, len(keys)):
            note = note + " " + values[i]
        note = unicodedata.normalize("NFC", note)
    return([lccn, header, note])

def fetch_sh(lccn, record):
    """pulls out form subdivisions for subject (sh) headings and scope note"""
    header = ""
    note = ""
    subfields = record["185"].subfields
    keys = subfields[::2]
    values = subfields[1::2]
    for i in range(0, len(keys)):
        header = header + "$" + keys[i] + " " + values[i] + " "
    header = header.strip()
    header = unicodedata.normalize("NFC", header)
    if record["680"] is not None and record["680"]["i"] is not None:
        subfields = record["680"].subfields
        keys = subfields[::2]
        values = subfields[1::2]
        for i in range(0, len(keys)):
            note = note + " " + values[i]
        note = unicodedata.normalize("NFC", note)
    return([lccn, header, note])


def processrecord(filename, type):
    """processes records in file based on type, whch is either "gf" or "sh" """
    marc_gen = reading_marc(filename)
    for record in marc_gen:
        lccn = lccnno(record)
        if lccn.startswith(type):
            if type == "sh" and record["185"] is not None and record["185"]["v"] is not None:
                yield(fetch_sh(lccn, record))
            elif type == "gf" and record["155"] is not None and record["155"]["a"] is not None:
                yield(fetch_gf(lccn, record))


def processfile(filename, type, csvfile):
    """looks at each record according to type to extract data to a csv file"""
    with open(csvfile, "w", newline='', encoding='utf-8') as myfile:
        wr = csv.writer(myfile)
        for line in processrecord(filename, type):
            wr.writerow(line)

if __name__ == "__main__":
    # command line arguments
    n = len(sys.argv)
    if n < 4:
        sys.exit("Missing arguments. \n python subjauth.py {input file path} [-sh {sh csv path}] [-gf {gf cvs path}]")
    
    sh = False
    gf = False
    shfile = ""
    gffile = ""
    filename = sys.argv[1]
    if not filename.endswith(".mrc"):
        sys.exit(f"{filename} not a valid path; must end in .mrc")

    for i in range(2,n):
        if sys.argv[i] == "-sh":
            sh = True
            if i+1 < n and sys.argv[i+1][0] != "-":
                shfile = sys.argv[i+1]
            else:
                sh = False
                print("No shfile specified")
        if sys.argv[i] == "-gf":
            gf = True
            if i+1 < n and sys.argv[i+1][0] != "-":
                gffile = sys.argv[i+1]
            else:
                gf = False
                print("No gffile specified")   
    if not (sh or gf):
        sys.exit("No authority record type specified")
    
    """functions that process the file by type"""
    if sh:
        processfile(filename, "sh", shfile)
    if gf:
        processfile(filename, "gf", gffile)