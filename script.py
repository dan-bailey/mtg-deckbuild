import csv
import json
import requests

def getOracleId(cardID):
    # send the cardID to Scryfall API and return the OracleID for use in the index
    oracleJSON = requests.get('https://api.scryfall.com/cards/' + cardID).json()
    return oracleJSON['oracle_id']

def getCardName(cardID):
    # clean up the card name in the CSV fields by using the CardID
    oracleJSON = requests.get('https://api.scryfall.com/cards/' + cardID).json()
    return oracleJSON['name']


### Pull CSV file into local memory, add OracleID and refresh Card Name

with open("le.csv") as csvfile:  
    data = csv.DictReader(csvfile)
    for row in data:
        # row['Name'] = getCardName(row['ScryfallID'])
        row['OracleID'] = getOracleId(row['ScryfallID'])
        row['Total Count'] = int(row['Number of Non-foil']) + int(row['Number of Foil'])
        print(row)

### De-duplicate the list by OracleID, including the Total Count
