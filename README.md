# AuthorityFiles
UPDATES in process

**Statement of Purpose**

This Python 3 program extracts data from MARC authority files and outputs it in a CSV format in order to manipulate the data in a spreadsheet.

It uses the specialzed Python library [pymarc](https://pymarc.readthedocs.io/en/latest/) to handle the [MARC Format](https://www.loc.gov/marc/) as well as several standard Python libraries.

The current functions cover:

+ extracting headings from [Library of Congress Subject Headings](https://www.loc.gov/aba/publications/FreeLCSH/freelcsh.html)
+ extracting form subdivisions from [Library of Congress Subject Headings](https://www.loc.gov/aba/publications/FreeLCSH/freelcsh.html)
+ extracting general subdivisions from [Library of Congress Subject Headings](https://www.loc.gov/aba/publications/FreeLCSH/freelcsh.html)
+ extracting headings from [Library of Congress Children Subject Headings (CYAC)](https://www.loc.gov/aba/publications/FreeCYAC/freecyac.html)
+ extracting all headings from the [Library of Congress Genre/Form Terms](https://www.loc.gov/aba/publications/FreeLCGFT/freelcgft.html)
+ extracting headings from [Library of Congress Demographic Group Terms](https://www.loc.gov/aba/publications/FreeLCdgt/freelcdgt.html)
+ extracting headings from [Library of Congress Medium of Performance Terms](https://www.loc.gov/aba/publications/FreeLCMPY/freelcmpt.html)



**How to run the program**

`python subjauth.py <input file path> -type [sh | fd | gd | dg | gf | sj | mp] -o <csv path> [-key <keyword string>]`

***Options***

| Option  | Explanation |
| ------------- | ------------- |
| -type sh  | Subject authority records  |
| -type fd  | Subject authority records for form subdivisions  |
| -type gd  | Subject authority records for general subdivisions  |
| -type sj  | Children's Subject authority records |
| -type gf  | Genre/Form authority records |
| -type dg  | Demographic Group Terms authority records |
| -type mp  | Medium of Performance Terms authority records |
| -o  | Output location and filename for csv file |
| -key  | Authority records Keyword search (phrases in quotes) |

**The CSV file**

The output of the CSV file contains three columns: 
+ LCCNs
  + MARC field 010 $a
+ the text of the heading
  + MARC field 1XX $a (with possible additional subfields) for headings in LCSH, LCGFT, LCDGT, CYAC, and LCMPT
  + MARC field 185 $v (with possible additional subfields $v or $x) for LCSH form subdivisions
  + MARC field 185 $x (with possible additional subfields $v or $x) for LCSH general subdivisions
+ scope note, if one exists
  + MARC field 680 ($i and possible $a subfields)

**Contributors**

+ Melanie Polutta: [@bibliotecaria](https://github.com/bibliotecaria)
+ Bobbi Fox: [@bobbi-SMR](https://github.com/bobbi-SMR)

 
