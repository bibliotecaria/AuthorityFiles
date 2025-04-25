# This program will search the authority file based on the identifier entered and then search the broader and narrower hierarchy of the term, depending on selection.

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
# recordset contains a list of hashes with a key of ID(LCCN). Hashes include ID, authlabel, variants, broader terms, narrower terms, reciprocal terms, and note from a MARC authority record.
authlabel_only = []
recordset = {}
idlist = []
direction = None

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
    value = None
    if "http://www.loc.gov/mads/rdf/v1#authoritativeLabel" not in sub:
        return(value)
    labels = sub["http://www.loc.gov/mads/rdf/v1#authoritativeLabel"]
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
    retval = []
    for note in notes:
        retval.append(note["@value"])
    return(" | ".join(retval))

def get_references(record):
    key = "http://www.loc.gov/mads/rdf/v1#variantLabel"
    variantlist = []
    reflist = [element for element in record if matches_key(key, element)]
    for ref in reflist:
        if "http://www.loc.gov/mads/rdf/v1#Temporal" not in ref["@type"]:
            var = ref[key][0]
            label = var["@value"]
            if label not in variantlist:
                variantlist.append(label)
    if len(variantlist) == 0:
        return("")
    return(" | ".join(variantlist))

def get_rel_ids(sub, has):
    # here is where we extract BTids, NTids, RTids
    #http://www.loc.gov/mads/rdf/v1#hasBroaderAuthority
    #http://www.loc.gov/mads/rdf/v1#hasNarrowerAuthority
    #http://www.loc.gov/mads/rdf/v1#hasReciprocalAuthority
    namespace = "http://www.loc.gov/mads/rdf/v1#has" + has
    can_append = ((direction == "N" and has == "NarrowerAuthority") or (direction == "B" and has == "BroaderAuthority"))
    if namespace not in sub:
        return([])
    auths = sub[namespace]
    ids = []
    for auth in auths:
        uri = auth["@id"]
        if uri is not None:
            id = uri.split("/")[-1]
            ids.append(id)
            if can_append and add_to_list(id):
                idlist.append(id)
    return(ids)

def add_labelonly(list):
    for r in list:
        if r not in authlabel_only:
            authlabel_only.append(r)

def process_sub(sub, labelonly = False):
    # here is where we extract data from sub-records of the record. For the broads, narrows, and reciprocals, it is just an ID.
    authlabel = get_authlabel(sub)
    if labelonly or authlabel is None:
        return(authlabel, "", [], [], [])
    notes = get_notes(sub)
    broads = get_rel_ids(sub, "BroaderAuthority")
    narrows = get_rel_ids(sub, "NarrowerAuthority")
    reciprocals = get_rel_ids(sub, "ReciprocalAuthority")
    add_labelonly(reciprocals)
    if direction == "N":
        add_labelonly(broads)
    else:
        add_labelonly(narrows)
    return(authlabel, notes, broads, narrows, reciprocals)

def requesting(url):
    #request will obtain data from the URL, loading it in JSON format
    record = None
    req = requests.get(url)
    if req.status_code == 200:
    # requests will follow redirects
        record = json.loads(req.text)
    else:
        print(f"Unable to retrieve [{url}]. Status code is {req.status_code}")
    return(record)

def handle_id(id):
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
        return(None, None)
    variants = get_references(record)
    sub_groups = []
    for sub in record:
        if sub["@id"] == baseuri:
            sub_groups.append(sub)
    #make sure that at least one match, report out if there is more than one match
    if len(sub_groups) == 0:
        print(f"No sub elements matching the URI [{baseuri}] for {id}.")
    elif len(sub_groups) > 1:
        print(f"{id} has more than one ID sub element group. First one will be processed.")
    return(variants, sub_groups)

def process_id(id, labelonly = False):
    # labelonly is used to tell us the IDs that don´t need information other than the authlabels
    variants, subs = handle_id(id)
    if variants is None and subs is None:
        print(f"Cannot find information for {id}. No variants or sub elements are found.")
        return()
    authlabel, notes, broads, narrows, reciprocals = process_sub(subs[0], labelonly)
    #authlabel is None means we cannot process this record
    if authlabel is None:
        print(f"Cannot find information for {id}. Missing authorized label. Possibly a deprecated record?")
        return()
    recordset[id] = {
        "authlabel":authlabel, 
        "notes":notes, 
        "broads":broads, 
        "narrows":narrows, 
        "reciprocals":reciprocals,
        "variants":variants}

def refine_recordset():
    for id in recordset.keys():
        for term in ["broads", "narrows", "reciprocals"]:
            terms = []
            for r_id in recordset[id][term]:
                if r_id in recordset:
                    terms.append(recordset[r_id]["authlabel"])
                else:
                    print(f"Cannot find term ID {r_id} for {id}.")
            recordset[id][term] = " | ".join(terms)

def process_list():
    for id in idlist:
        process_id(id)
    for r_id in authlabel_only:
        if r_id not in recordset.keys():
            process_id(r_id, True)

def write_csv():
    heads = ["authlabel", "variants", "broads", "narrows", "reciprocals", "notes"]
    try:
        with open(csvfile, "w", newline='', encoding='utf-8') as myfile:
            wr = csv.writer(myfile)
            wr.writerow(["LCCN", "Heading", "Variants", "Broader", "Narrower", "Related", "Notes"])
            for id in idlist:
                line = [id]
                for h in heads:
                    line.append(recordset[id][h])
                wr.writerow(line)
    except Exception as e:
        sys.exit(f"Problem found in writing to {csvfile}: {e.__class__.__doc__} [{e.__class__.__name__}]")


if __name__ == "__main__":
    # command line arguments
    parser = argparse.ArgumentParser(description='Get options.')
    parser.add_argument("-o", help="Path to csv file output required.", required=True, metavar="output")
    parser.add_argument("-id", help="Enter the LCCN. E.g. \"sh 85234587\"")
    parser.add_argument("-direct", help="Enter N or B to search in the direction of Narrower or Broader Terms.")
    args = parser.parse_args()
    direction = args.direct
    if direction != "N" and direction != "B":
        print("Direction must be N or B.")
        sys.exit(1)
    id = args.id.replace(" ","")
    idlist.append(id)
    process_list()
    refine_recordset()
    if not recordset:
        print("No information processed.")
        sys.exit(0)
    csvfile = args.o
    write_csv()
    print(f"CSV written to {args.o}")
    
#Readme file