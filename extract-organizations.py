# Code to extract organization names from the 'waarde' field of Parlement.com position data
# @author Frank Takes - takes@uva.nl
# @dependencies: Python 2, Pandas
# @run code using 'python filename.csv' 

import sys
import pandas as pd
import string

# read the data
df = pd.read_csv(str(sys.argv[1]),sep=",")
df2 = df

# some stats before and after filtering non "neven" positions
print df.shape
df = df[df.rubriek >= 3500]  
print df.shape

# capitalize some stuff that should be capitalized for proper filtering later
df['waarde'] = df['waarde'].str.replace('gemeente', 'Gemeente', case=True)
df['waarde'] = df['waarde'].str.replace('burgemeester', 'Burgemeester', case=True)

# create a lower case version of the "waarde" column
df['waardelower'] = df['waarde'].str.lower()

# remove forbidded strings related to party/political positions
forbiddenstrings = [
'vvd', 'cda', 'pvda', 'd66', 'christenunie', 'groenlinks', 'lpf', 
'jovd', 'jonge socialisten', 'cdja', 'volkspartij', 'kvp', 
'politiek leider',
'provinciale staten', 'eerste kamer', 'tweede kamer', 'parlement', #'gemeenteraad'
'partijbestuur', 'minister', 'formateur', 'informateur', 'raad van state', 'staatssecretaris', 
'ambteloos', 'tijdelijk vervangen'
]
forbiddenregex = '|'.join(forbiddenstrings)
df = df[df['waardelower'].str.match('(.*(' + forbiddenregex + ').*)').str.len() == 0] 

# some stats after filtering out political positions
print "\n"
print df.shape

# filter the type of position. order seems important, "plaatsvervangend voorzitter" will not be filtered if it is preceded by "voorzitter"
typestring = [
' lid', '^lid', 'plaatsvervangend voorzitter', 'voorzitter', 'columnist', 'permanent vertegenwoordiger', 
'vertegenwoordiger', 'medewerker', 'directeur', 'adviseur', 'eindredacteur', 'gastdocent', 'fellow', 'manager', 'officier', 
'dagelijks bestuur', 'raad van bestuur', 'algemeen bestuur', 'bestuur', 'raad van advies', 'raad van toezicht', 'raad van commissarissen', 'curatorium', 
]
typeregex = '|'.join(typestring)	
df['organisatie'] = df['waarde'].str.replace('(\S*(' + typeregex + ')\S*)', '', case=False)

# organization starts at first occurence of uppercase
df['organisatie'] = df['organisatie'].str.lstrip(string.lowercase + ' ,().') 
df['organisatie'] = df['organisatie'].str.replace('(\(|\)|\'|\"|\.|\-|\/)', ' ')
df['organisatie'] = df['organisatie'].str.replace('  ', ' ')
df['organisatie'] = df['organisatie'].str.strip()

# type is whatever remains after removing the previously extracted organization
df['type'] = df.apply(lambda x: (x['waarde'].replace(x['organisatie'],"")).lower(), axis=1) 
df['type'] = df['type'].str.strip()

# list some stats to see how it went
print df['type'].value_counts()[:40]
print "\n"
print df['organisatie'].value_counts()[:40]
print "\n"

# merge with original dataset again (from which we removed <= 3500 and party/political positions)
df = df.combine_first(df2)

# output to csv
df.to_csv('detailsfiltered.csv', sep=',', columns=['b1-nummer', 'rubriek', 'organisatie', 'type', 'waarde', 'datum', 'toelichting'], index=False)

