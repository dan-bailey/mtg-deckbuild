import csv
import json
import requests
import sys
import pandas as pd
import datetime
from IPython.display import display

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

def getCardCount(df, oracle):
    # return the card quantity from a dataframe for the given OracleID
    row_num = df[df['OracleID'] == oracle].index
    if row_num.empty:
        return 0
    else:
        row_num = row_num[0]
        return int(df.loc[row_num, 'Quantity'])

def printTime():
    return datetime.datetime.now().strftime("%H:%M:%S")

### Pull CSV file into local memory, add OracleID and create Total Card Count
print(f"({printTime()}) Loading card library.")
cardLibrary = pd.read_csv('le.csv')

### Filter down to the pertinent columns needed
print(f"({printTime()}) Filtering columns.")
cardLibrary = cardLibrary.filter(['Name', 'CardID', 'Number of Non-foil', 'Number of Foil', 'ScryfallID']) 

### Add the foil and non-foil counts into a single column
print(f"({printTime()}) Consolidating counts.")
cardLibrary["Quantity"] = cardLibrary["Number of Non-foil"] + cardLibrary["Number of Foil"]

### Drop the foil/non-foil columns as they're unnecessary
print(f"({printTime()}) Dropping unnecessary columns.")
cardLibrary = cardLibrary.drop(columns=['Number of Non-foil', 'Number of Foil'])

### Grab the Oracle IDs for each card
print(f"({printTime()}) Adding Oracle IDs. This could take awhile.")
cardLibrary["OracleID"] = cardLibrary["ScryfallID"].apply(getOracleId)


## Report on the card library progress...
print(f"({printTime()}) There were {str(cardLibrary.shape[0])} rows imported from the CSV.")

### Deduplicating the card library
print(f"({printTime()}) Now deduplicating the card library.")
## Group by OracleID and sum the Quantity, then drop the dupes and reindex
cardLibrary["Quantity"] = cardLibrary.groupby(['OracleID'])['Quantity'].transform('sum')
cardLibrary = cardLibrary.drop_duplicates(subset=['OracleID']).reset_index()  

### Final report on the card library size
print(f"({printTime()}) There are now {str(cardLibrary.shape[0])} cards in the library.")

### Grab the Archidekt decklist
print(" ")
print(f"({printTime()}) Attempting to build a decklist for Archidekt ID: {archidektID}.")
print(" ")
### Grab the Archidekt decklist
jsondecklist = requests.get(f'https://archidekt.com/api/decks/{archidektID}/').json()
decklist = jsondecklist['cards']

### Create a new dataframe to hold the decklist 
shoppingList = []
haveList =[]
archidekt = pd.DataFrame(columns=['Name', 'QuantityNeeded', 'OracleID', 'Have'])
for card in decklist:
    name = card['card']['oracleCard']['name']
    needed = card['quantity']
    oracle = card['card']['oracleCard']['uid']
    have = getCardCount(cardLibrary, card['card']['oracleCard']['uid'])
    if have < needed:
        splats = "*** "
        shoppingList.append([name, needed - have])
    else:
        splats =""
        haveList.append([name, needed, have])
    # print(f"{splats}{needed}x {name} (Have: {have})")
print(" ")

### Print out the shopping list
print("SHOPPING LIST")
for item in shoppingList:
    print(f"{item[1]}x {item[0]}")

print("HAVE LIST")
for item in haveList:
    print(f"{item[1]}x {item[0]} (Have: {item[2]})")
