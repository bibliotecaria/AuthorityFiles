# Processing Authority files via Linked Data API 

**Statement of Purpose**

This program, given an authority record ID, will access the authority file at the API of https://id.loc.gov. The rows of the output CSV file includes information about the requested record, plus any records that reflect the hierarchy of narrower or broader terms, depending on the direction requested.

To run the search, enter the identifier (e.g. **sh 89003642**) for the term you want to search, the direction of the hierarchy crawl, and the path of the output file.

The current functions will search these heading types:

+ [Library of Congress Subject Headings](https://www.loc.gov/aba/publications/FreeLCSH/freelcsh.html)
+ [Library of Congress Children Subject Headings (CYAC)](https://www.loc.gov/aba/publications/FreeCYAC/freecyac.html)
+ [Library of Congress Genre/Form Terms](https://www.loc.gov/aba/publications/FreeLCGFT/freelcgft.html)
+ [Library of Congress Demographic Group Terms](https://www.loc.gov/aba/publications/FreeLCdgt/freelcdgt.html)
+ [Library of Congress Medium of Performance Terms](https://www.loc.gov/aba/publications/FreeLCMPY/freelcmpt.html)

**How to run the program**

`python process-ar.py --help` will show all options

Here is the full syntax:

`python process-ar.py -id <LCCN> -o <csv output file> -direct [B | N]`

***Options***

| Option  | Explanation |
| ------------- | ------------- |
| -direct B  | Searches broader terms  |
| -direct N  | Searches narrower terms  |

**The CSV file**

The output of the CSV file contains three columns: 
+ LCCNs (MARC field 010 $a)
  + the LCCN of the originally requested record
  + the LCCN of every record that is either the broader or narrower terms, depending on requested direction
+ the authorized label (MARC field 1XX $a (with possible additional subfields) for headings in LCSH, LCGFT, LCDGT, CYAC, and LCMPT)
+ all variant labels (MARC 4XX fields), delimited by **|**
+ all authorized labels of broader terms, delimited by **|**
+ all authorized labels of narrower terms, delimited by **|**
+ all authorized labels of related terms, delimited by **|**
+ scope note(s), if there are any (MARC field 680 ($i and possible $a subfields)), delimited by **|**

**Contributors**

+ Melanie Polutta: [@bibliotecaria](https://github.com/bibliotecaria)
+ Bobbi Fox: [@bobbi-SMR](https://github.com/bobbi-SMR)

 
