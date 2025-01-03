'''This program will search the authority file based on the identifier entered 
and then search up and down the hierarchy of the term.
To run the search, extract the id.loc.gov URI for the term you want to search, and plug that into the program that will be created.
	1. JSON file is organized as an array of dicts. We are looking for the specific one in which the last part of the character of the @id key matches the LCCN that we have plugged in.
		a. Make sure to remove space from LCCN.
	2. Get a heading ID (the LCCN transformed for the URI) and fetch the JSON based on that ID
	3. Identify the hash (or dict) in the JSON array that contains the information desired.
		a. Go through list of dicts until we find the one that matches the @ID key matches the heading
         ID we've entered.
	4. Establish separate functions for extracting the information from the 010, 1XX, 4XX, 5XX, NTs, and 680.
Need to maintain a list of already-processed headings so as not to repeat recursion.
'''

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

def matches_key(key, element):
    if key in element:
        return True
    else:
        return False

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

def get_references(record):
    #http://www.loc.gov/mads/rdf/v1#variantLabel
    #http://www.loc.gov/mads/rdf/v1#Temporal
    #http://www.loc.gov/mads/rdf/v1#ComplexSubject
    #http://www.loc.gov/mads/rdf/v1#Topic
    key = "http://www.loc.gov/mads/rdf/v1#variantLabel"
    variantlist = []
    # TODO get references is not working
    reflist = [element for element in record if matches_key(key, element)]
    for ref in reflist:
        if "http://www.loc.gov/mads/rdf/v1#Temporal" not in ref["@type"]:
            var = ref[key][0]
            label = var["@value"]
            if label not in variantlist:
                variantlist.append(label)
    return(" | ".join(variantlist))


def process_record(sub):
    authlabel = get_authlabel(sub)
    variants = get_references(sub)


def requesting(url):
    record = None
    req = requests.get(url)
    if req.status_code == 200:
    # requests will follow redirects
        record = json.loads(req.text)
    # TODO: log status errors
    return(record)

def process_uri(uri):
    # construct URL from URI
    temp = uri.split(":")
    url = "https:" + temp[1] + ".madsrdf.json"
    # get record from API
    # create sub
    # call process_record, which will return a hash
    # put hash on hash stack by URI as key
    return(None)

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
    record = requesting(url)
    if record is None:
        print("unable to find record")
        sys.exit()
    matches = []
    for sub in record:
        if sub["@id"] == baseuri:
            matches.append(sub)
    #make sure that at least one match, report out of there is more than one match
    if len(matches) == 0:
        sys.exit()
    elif len(matches) > 1:
        print(f"{baseurl} has more than one ID match")
    process_record(matches[0])
    csvfile = args.o
