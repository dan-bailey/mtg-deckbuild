import csv
import json
import requests
import sys

### grab arguments (which should be archidekt deck IDs)
archidektID = sys.argv[1]

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

def howMany(oid, targetList):
    for card in targetList:
        if card['OracleID'] == oid:
            return card['TotalCards']
        else:
            return 0

### Pull CSV file into local memory, add OracleID and create Total Card Count
print("Loading CSV file into memory...")
listCount = 0
cardList = []
with open("le.csv") as csvfile:  
    data = csv.DictReader(csvfile)
    for row in data:
        insertCard = {
            'Name': row['Name'],
            'ScryfallID': row['ScryfallID'],
            'OracleID': getOracleId(row['ScryfallID']),
            'TotalCards': int(row['Number of Non-foil']) + int(row['Number of Foil'])
        }
        cardList.append(insertCard)

### Set Up Merged List
mergedList = []

### Let's get all the single cards into the merged list first
print("Creating new list with single cards...")
final = len(cardList)
for x in range(0, final):
    card = cardList[x]
    target = card['OracleID']
    locs = getLocations(target, cardList)
    numLocs = len(locs)
    if numLocs == 1:
        newCard = {
            'Name': card['Name'],
            ## 'ScryfallID': card['ScryfallID'],
            'OracleID': card['OracleID'],
            'TotalCards': card['TotalCards']
        }
        mergedList.append(newCard)

### Let's create a merged card of multiple cards
print("Merging duplicate cards into master list...")
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

totalCardCount = 0
for card in mergedList:
    totalCardCount += card['TotalCards']
    print(f"{card['Name']} - {card['TotalCards']}")
print(f"Unique cards: {len(mergedList)}")
print(f"Total cards: {totalCardCount}")
print(f"Each card has an average of {totalCardCount / len(mergedList)} copies.")
print("")
### Free up memory by wiping out original card list
cardList = []

### Write the merged list to a new CSV file
print("Writing merged list to CSV file...")
with open('merged.csv', mode='w', newline='') as csvfile:
    fieldnames = ['Name', 'ScryfallID', 'OracleID', 'TotalCards']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for card in mergedList:
        writer.writerow(card)

print(f"Attemping to build a decklist for Archidekt ID: {archidektID}.")
print(" ")
### Grab the Archidekt decklist
jsondecklist = requests.get(f'https://archidekt.com/api/decks/{archidektID}/').json()
decklist = jsondecklist['cards']
totalArchidektCards = 0
for card in decklist:
    totalArchidektCards += card['quantity']

cleanArchidekt = []
### Start reporting re: feasibility
print(f"Report for: {jsondecklist['name']} ({archidektID})")
print(f"Link to Archidekt Deck: https://archidekt.com/decks/{archidektID}")
print(f"Total Cards in Archidekt Deck: {totalArchidektCards}")
for card in decklist:
    # show oraclename and quantity
    newCard = {
        'Name': card['card']['oracleCard']['name'],
        'OracleID': card['card']['oracleCard']['uid'],
        'RequiredQuantity': card['quantity'],
        'HaveQuantity': howMany(card['card']['oracleCard']['uid'], mergedList)
    }
    cleanArchidekt.append(newCard)

haveCards = 0
for card in cleanArchidekt:
    # print(f"{card['Name']} - Required: {card['RequiredQuantity']} - Have: {card['HaveQuantity']}")
    if card['HaveQuantity'] >= card['RequiredQuantity']:
        haveCards += 1

print(" ")
print(f"You have {haveCards} out of {len(cleanArchidekt)} cards in the deck, or {haveCards / len(cleanArchidekt) * 100}%.")

