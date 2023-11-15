# AuthorityFiles

**Statement of Purpose**

This Python 3 program extracts data from MARC authority files and outputs it in a CSV format in order to manipulate the data in a spreadsheet.

It uses the specialzed Python library [pymarc](https://pymarc.readthedocs.io/en/latest/) to handle the [MARC Format](https://www.loc.gov/marc/) as well as several standard Python libraries.

The current functions cover:

+ extracting form subdivisions from [Library of Congress Subject Headings](https://www.loc.gov/aba/publications/FreeLCSH/freelcsh.html)
+ extracting all headings from the [Library of Congress Genre/Form Terms](https://www.loc.gov/aba/publications/FreeLCGFT/freelcgft.html)

**How to run the program**

`python subjauth.py {input file path} [-sh {sh csv path}] [-gf {gf cvs path}]`

***Options***

| Option  | Explanation |
| ------------- | ------------- |
| -sh  | Subject authority records; requires a filepath to output csv file  |
| -gf  | Genre/Form authority records; requires a filepath to output csv file |

**The CSV file**

The output of the CSV file contains three columns: 
+ LCCNs
  + MARC field 010 $a
+ the text of the heading
  + MARC field 185 $v (with possible additional subfields $v or $x) for LCSH form subdivisions
  + MARC field 155 $a for LCGFT terms
+ scope note, if one exists
  + MARC field 680 ($i and possible $a subfields)

**Contributors**

+ Melanie Polutta: [@bibliotecaria](https://github.com/bibliotecaria)
+ Bobbi Fox: [@bobbi-SMR](https://github.com/bobbi-SMR)

 
