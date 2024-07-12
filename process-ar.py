import sys
import requests
import json
import argparse
import csv

PREFIX="https://id.loc.gov/authorities/"
TYPE={"mp":"performanceMediums/",
      "sh":"subjects/", 
      "sj":"childrensSubjects/", 
      "dg":"demographicTerms/", 
      "gf":"genreForms/"}

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
        baseurl = PREFIX + TYPE[id[0:2]] + id
        url = baseurl + ".madsrdf.json"
    print(url)
    req = requests.get(url)
    record = json.loads(req.text)
    for sub in record:
        if sub["@id"] == baseurl:
            print("yeah")
            #why us baseurl not there? (July 12, 2024 question)
    csvfile = args.o
