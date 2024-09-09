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

def getLocations(oid, bigList):
    idx = 0
    locs = []
    for card in bigList:
        if card['OracleID'] == oid:
            locs.append(idx)
        idx += 1
    return locs

def isInList(oid, mList):
    if len(getLocations(oid, mList)) > 0:
        return True
    else:
        return False

### Pull CSV file into local memory, add OracleID and create Total Card Count
listCount = 0
cardList = []
with open("le.csv") as csvfile:  
    data = csv.DictReader(csvfile)
    for row in data:
        oid = getOracleId(row['ScryfallID'])
        insertCard = {
            'Name': row['Name'],
            'ScryfallID': row['ScryfallID'],
            'OracleID': oid,
            'TotalCards': int(row['Number of Non-foil']) + int(row['Number of Foil'])
        }
        cardList.append(insertCard)

### Set Up Merged List
mergedList = []

### Let's get all the single cards into the merged list first
final = len(cardList) - 1
for x in range(0, final):
    card = cardList[x]
    target = card['OracleID']
    locs = getLocations(target, cardList)
    numLocs = len(locs)
    print (f"{card['Name']} has {numLocs} entries at {locs}.")
    if numLocs == 1:
        print(f"Removing {card['Name']} from the list at location {x}.")
        newCard = {
            'Name': card['Name'],
            'ScryfallID': card['ScryfallID'],
            'OracleID': card['OracleID'],
            'TotalCards': card['TotalCards']
        }
        mergedList.append(newCard)

### Let's create a merged card of multiple cards
for card in cardList:
    if not isInList(card['OracleID'], mergedList):
        locs = getLocations(card['OracleID'], cardList)
        if len(locs) > 1:
            print(f"Creating a merged card for {card['Name']}.")
            total = 0
            for loc in locs:
                total += cardList[loc]['TotalCards']
            newCard = {
                'Name': card['Name'],
                'ScryfallID': card['ScryfallID'],
                'OracleID': card['OracleID'],
                'TotalCards': total
            }
            mergedList.append(newCard)

### Checking to see if it works as intended
print(" ")
print ("Merged Card List:")
totalCardCount = 0
for card in mergedList:
    print(f"{card['Name']} has {card['TotalCards']} cards.")
    totalCardCount += card['TotalCards']
print(f"Total Card Count: {totalCardCount}")