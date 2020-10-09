import csv

pays = []
with open('countries.csv', newline='') as csvfile:
   reader = csv.DictReader(csvfile, delimiter=';')   # Objet DictReader (itérateur)
   for row in reader:
      pays.append(dict(row))     # Conversion du type OrderedDict en dictionnaire
'''
Dollars_Code = [p['Currency_Code'] for p in pays if 'Dollar' in p['Currency_Name']]
Dollars_Countries = [p['Name'] for p in pays if 'Dollar' in p['Currency_Name']]
Dollars = zip(Dollars_Countries, Dollars_Code)
print(list(Dollars))
print([p['Name'] for p in pays if int(p['Population'])>100000000])

def cle_superficie(p):
   return float(p['Area'])
pays.sort(key=cle_superficie, reverse=True)
sorted([(p['Name'], float(p['Area'])) for p in pays], key=lambda p:p[1], reverse=True)[:5]
print([(p['Name'], p['Area'])for p in pays[:5]])
'''
print(sorted([(p['Name'], float(p['Population'])) for p in pays], key=lambda p:p[1])[:10])