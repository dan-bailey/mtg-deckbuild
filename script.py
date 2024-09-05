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


### Pull CSV file into local memory, add OracleID and create Total Card Count
listCount = 0
cardList = []
with open("le.csv") as csvfile:  
    data = csv.DictReader(csvfile)
    for row in data:
        cardList.append({
            'Name': row['Name'],
            'ScryfallID': row['ScryfallID'],
            'OracleID': getOracleId(row['ScryfallID']),
            'TotalCards': int(row['Number of Non-foil']) + int(row['Number of Foil'])
        })

### De-duplicate the list by OracleID, including the Total Count Merge Down
print("Total Rows: " + str(len(cardList)))
dedupedCardList = []
for card in cardList:
    target = card['OracleID']
    print("Checking: " + card['Name'] + " (" + card['OracleID'] + ")")
    for cardtarget in cardList:
        if cardtarget['OracleID'] == target:
            card['TotalCards'] += cardtarget['TotalCards']
            cardList.remove(cardtarget)
            print("Total Cards: " + str(card['TotalCards']) + "\n\n")
            ## This logic is busted. Come back and fix this big-time.