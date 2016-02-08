# Code to extract organization names from the 'waarde' field of Parlement.com position data
# @author Frank Takes - takes@uva.nl
# @dependencies: Python 2, Pandas
# @run code using: 		python details.csv
# after running once 	iconv -f utf8 -t ascii//TRANSLIT originalfile > details.csv   replace all x with umlaut/accent/etc by plain x   (with x in klinkers)


import sys
import pandas as pd
import string
from unidecode import unidecode

# some custom "dictionaries"
positions = [
' lid', '^lid', 'vicevoorzitter',  'vice voorzitter', 'vicepresident', 'plaatsvervangend voorzitter', 'algemeen voorzitter', 'voorzitter', 'columnist', 'permanent vertegenwoordiger', 'secretaris', 'bedrijfs economisch medewerker', 'wetenschappelijk medewerker', 'medewerker', 'medewerkster', 'penningmeester', 
'vertegenwoordiger', 'medewerker', 'concern directeur', 'directeur', 'senior adviseur', 'organisatie adviseur', 'intern adviseur',  'adviseur', 'eindredacteur', 'gastdocent', 'fellow', 'manager', 'officier'
]
bodies = [
'dagelijks bestuur', 'raad van bestuur', 'algemeen bestuur', 'bestuur', 'raad van advies', 'raad van toezicht', 'raad van commissarissen', 'curatorium', 'regiegroep', 'comite van aanbeveling'
]
parties = [
'vvd', 'cda', 'pvda', 'd66', 'christenunie', 'groenlinks', 'lpf', 
'jovd', 'jonge socialisten', 'cdja', 'volkspartij', 'kvp', 'arp', 
'politiek leider',
'provinciale staten', 'eerste kamer', 'tweede kamer', 'parlement', #'gemeenteraad'
'partijbestuur', 'minister', 'formateur', 'informateur', 'raad van state', 'staatssecretaris', 
'ambteloos', 'tijdelijk vervangen'
]

# read the data
df = pd.read_csv(str(sys.argv[1]),sep=",")
df2 = df

# print some stats before and after filtering non "neven" positions
print (df.shape)
df = df[df.rubriek >= 3500]  
print (df.shape)

# capitalize some stuff that should be capitalized for proper filtering later
df['waarde'] = df['waarde'].str.replace('gemeente', 'Gemeente', case=True)
df['waarde'] = df['waarde'].str.replace('waarnemend burgemeester', 'Waarnemend Burgemeester', case=True)
df['waarde'] = df['waarde'].str.replace('burgemeester', 'Burgemeester', case=True)

# create a lower case version of the "waarde" column
df['waardelower'] = df['waarde'].str.lower()

# remove forbidded strings related to party/political positions
forbiddenstrings = parties
forbiddenregex = '|'.join(forbiddenstrings)
df = df[df['waardelower'].str.match('(.*(' + forbiddenregex + ').*)').str.len() == 0] 

# some stats after filtering out political positions
print ("\n")
print (df.shape)

# filter the type of position. order seems important, "plaatsvervangend voorzitter" will not be filtered if it is preceded by "voorzitter"
typestring = positions + bodies
typeregex = '|'.join(typestring)	
df['organisatie'] = df['waarde'].str.replace('(\S*(' + typeregex + ')\S*)', '', case=False)

# organization starts at first occurence of uppercase
df['organisatie'] = df['organisatie'].str.lstrip(string.lowercase + ' ,().') 
df['organisatie'] = df['organisatie'].str.replace('(\(|\)|\'|\"|\.|\-|\/)', ' ')
df['waarde'] = df['waarde'].str.replace('(\(|\)|\'|\"|\.|\-|\/)', ' ')
df['waarde'] = df['waarde'].str.replace('  ', ' ')
df['organisatie'] = df['organisatie'].str.replace('  ', ' ')

# remove everything after the comma
def delete_after_comma(x):
    ind = x.find(",")
    if ind > 0:
        return x[:x.find(",")]
    else: return x
df['organisatie'] = df['organisatie'].str.strip()

# type is whatever remains after removing the previously extracted organization
df['positionbody'] = df.apply(lambda x: (x['waarde'].replace(x['organisatie'],"")).lower(), axis=1) 
df["organisatie"] = df["organisatie"].apply(lambda x: delete_after_comma(x))
df["positionbody"] = df["positionbody"].apply(lambda x: delete_after_comma(x))
df['positionbody'] = df['positionbody'].str.replace('(\(|\)|\'|\"|\,|\.|\-|\/)', ' ')
df['positionbody'] = df['positionbody'].str.strip()
df['positionbody'] = df['positionbody'].str.replace('  ', ' ')

# filter the body by excluding the position
positionstring = positions
positionregex = '|'.join(positionstring)	
df['body'] = df['positionbody'].str.replace('(^\S*(' + positionregex + ')\S*)', '', case=False)

# filter the position by excluding the body from the positionbody
df['position'] = df.apply(lambda x: (x['positionbody'].replace(x['body'],"")).lower(), axis=1) 

# clean it all
df['body'] = df['body'].str.strip()
df['body'] = df['body'].str.replace('  ', ' ')
df['position'] = df['position'].str.strip()
df['position'] = df['position'].str.replace('  ', ' ')

# print some stats
print (df['positionbody'].value_counts()[:40])
print ("\n")
print (df['position'].value_counts()[:40])
print ("\n")
print (df['body'].value_counts()[:40])
print ("\n")
print (df['organisatie'].value_counts()[:40])
print ("\n")

# merge with original dataset again (from which we removed < 3500 and party/political positions)
df = df.combine_first(df2)

# output to csv
df.to_csv('detailsfiltered.csv', sep=',', columns=['b1-nummer', 'rubriek', 'position', 'body', 'positionbody', 'organisatie', 'waarde', 'datum', 'toelichting'], index=False)

