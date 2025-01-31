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
# recordset contains a list of hashes with two keys: URI, processed(Boolean)
reciplist = []
recordset = {}
# TODO how to handle constantly changing list of hashes
idlist = []
# here is the list of LCCNs
start_id = None

def add_to_list(id):
    add = True
    if id in idlist or id in recordset.keys():
        add = False
    return(add)

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
    if "http://www.loc.gov/mads/rdf/v1#note" not in sub:
        return("")
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
    if "http://www.loc.gov/mads/rdf/v1#variantLabel" not in record:
        return("")
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

def get_rel_ids(sub, has):
    # here is where we extract BTids, NTids, RTids
    #http://www.loc.gov/mads/rdf/v1#hasBroaderAuthority
    #http://www.loc.gov/mads/rdf/v1#hasNarrowerAuthority
    #http://www.loc.gov/mads/rdf/v1#hasReciprocalAuthority
    namespace = "http://www.loc.gov/mads/rdf/v1#has" + has
    if namespace not in sub:
        return([])
    auths = sub[namespace]
    ids = []
    for auth in auths:
        uri = auth["@id"]
        if uri is not None:
            id = uri.split("/")[-1]
            ids.append(id)
            if add_to_list(id):
                idlist.append(id)
    return(ids)

def process_sub(sub):
    # here is where we extract data from subs of the record
    authlabel = get_authlabel(sub)
    notes = get_notes(sub)
    broads = get_rel_ids(sub, "BroaderAuthority")
    narrows = get_rel_ids(sub, "NarrowerAuthority")
    reciprocals = get_rel_ids(sub, "ReciprocalAuthority")
    for r in reciprocals:
        if r not in reciplist:
            reciplist.append(r)
    return(authlabel, notes, broads, narrows, reciprocals)

def requesting(url):
    record = None
    req = requests.get(url)
    if req.status_code == 200:
    # requests will follow redirects
        record = json.loads(req.text)
    # TODO log status errors
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

def handle_id(id):
    # needs to return status because sys.exit won't work here -- need TRUE/FALSE for testing
    # take id and make full madsrdf.json record from which to extract data via API
    id = id.replace(" ","")
    if id[0:2] not in TYPE:
        print(f"Type {id[0:2]} not supported ({id}).")
        return(None, None)
    else:
        baseurl = "https" + PREFIX + TYPE[id[0:2]] + id
        baseuri = "http" + PREFIX + TYPE[id[0:2]] + id
        url = baseurl + ".madsrdf.json"
    print(url)
    record = requesting(url)
    if record is None:
        print("unable to find record")
        return(None, None)
    variants = get_references(record)
    sub_groups = []
    for sub in record:
        if sub["@id"] == baseuri:
            sub_groups.append(sub)
    #make sure that at least one match, report out of there is more than one match
    if len(sub_groups) == 0:
        print(f"No sub groups in {id}.")
    elif len(sub_groups) > 1:
        print(f"{id} has more than one ID sub group")
    return(variants, sub_groups)
    # needs to move process_record(sub_groups[0])

def process_id(id):
    # here is where we create URI and URL (in subroutine), get data, also subprocessing for data
    variants, subs = handle_id(id)
    if variants is None and subs is None:
        print("Cannot find information")
        return()
    # TODO define what is returned
    # recordset needs LCCN, authlabel, variants, notes, BTid, NTid, RTid
    authlabel, notes, broads, narrows, reciprocals = process_sub(subs[0])
    # recordset["sh3443"] = {'auth'='foo', 'variant'=[alist],'notes'=[listof notes], 'bIds='sh233|sh99'}
    recordset[id] = {
        "authlabel":authlabel, 
        "notes":notes, 
        "broads":broads, 
        "narrows":narrows, 
        "reciprocals":reciprocals,
        "variants":variants}

def refine_recordset():
    # TODO find authlabel for BTid, NTid, RTid
    for id in recordset.keys():
        for term in ["broads", "narrows", "reciprocals"]:
            termstring = ""
            for r_id in recordset[id][term]:
                termstring += recordset[r_id]["authlabel"] + " | " 
            recordset[term] = termstring

def process_list():
    for id in idlist:
        process_id(id)
    for r in reciplist:
        #handle ids of reciplist to get authlabel, check to make sure not already called
        pass


def write_csv():
    # LCCN, authlabel, variantlabel, broader terms, narrower terms, reciprocal terms, notes
    pass

if __name__ == "__main__":
    # command line arguments
    parser = argparse.ArgumentParser(description='Get options.')
    parser.add_argument("-o", help="Path to csv file output required.", required=True, metavar="output")
    parser.add_argument("-id", help="Enter the LCCN. E.g. \"sh 85234587\"")
    args = parser.parse_args()
    #print("we parsed")
    id = args.id.replace(" ","")
    start_id = id
    idlist.append(id)
    process_list()
    refine_recordset()
    # TODO write out recordset
    csvfile = args.o




"""     variants, sub_groups = handle_id(id)
    # TODO handle errors
    process_record(sub_groups[0])
 """