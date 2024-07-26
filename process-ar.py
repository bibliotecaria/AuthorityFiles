import sys
import requests
import json
import argparse
import csv


PREFIX="://id.loc.gov/authorities/"
TYPE={"mp":"performanceMediums/",
      "sh":"subjects/", 
      "sj":"childrensSubjects/", 
      "dg":"demographicTerms/", 
      "gf":"genreForms/"}
recordset = {}

def get_authlabel(sub):
    #http://www.loc.gov/mads/rdf/v1#authoritativeLabel
    labels = sub["http://www.loc.gov/mads/rdf/v1#authoritativeLabel"]
    value = None
    for label in labels:
        if label["@language"] == "en":
            value = label["@value"]
    return(value)

def get_lccn(sub):
    #"http://id.loc.gov/vocabulary/identifiers/lccn"
    lccn = sub["http://id.loc.gov/vocabulary/identifiers/lccn"][0]["@value"]
    #LOOK up a record that has a 010 $z old LCCN to see if we need an if statement
    return(lccn)

def get_notes(sub):
    #http://www.loc.gov/mads/rdf/v1#note
    notes = sub["http://www.loc.gov/mads/rdf/v1#note"]
    retval = ""
    for note in notes:
        retval = note["@value"] + " | "
    return(retval)

def get_references(sub):
    #http://www.loc.gov/mads/rdf/v1#variantLabel
    seeref = sub["http://www.loc.gov/mads/rdf/v1#variantLabel"]
    return(None)


def process_record(sub):
    authlabel = get_authlabel(sub)

if __name__ == "__main__":
    # command line arguments
    parser = argparse.ArgumentParser(description='Get options.')
    parser.add_argument("-o", help="Path to csv file output required.", required=True, metavar="output")
    parser.add_argument("-id", help="Enter the LCCN. E.g. \"sh 85234587\"")
    args = parser.parse_args()
    #print("we parsed")
    id = args.id.replace(" ","")
    if id[0:2] not in TYPE:
        sys.exit(f"Type {id[0:2]} not supported.")
    else:
        baseurl = "https" + PREFIX + TYPE[id[0:2]] + id
        baseuri = "http" + PREFIX + TYPE[id[0:2]] + id
        url = baseuri + ".madsrdf.json"
    print(url)
    req = requests.get(url)
    #requests will follow redirects
    record = json.loads(req.text)
    for sub in record:
        if sub["@id"] == baseuri:
            print("yeah")
    csvfile = args.o
