import os
import sqlite3
import csv
import json
import requests
import sys
import pandas as pd
import datetime
import colorama
import logging

### FUNCTIONS

def getOracleId(cardID):
    # check to see if the cardID is in the cache
    cursor = db.execute('SELECT oracle_id FROM oracle_ids WHERE card_id = ?', (cardID,))
    logging.info(f"Type of DB results: {type(cursor)}")
    logging.info(f"Results of DB scan: {cursor}")
    # send the cardID to Scryfall API and return the OracleID for use in the index
    # oracleJSON = requests.get('https://api.scryfall.com/cards/' + cardID).json()
    # return oracleJSON['oracle_id']
    return "derp"


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
    
### grab arguments (which should be archidekt deck IDs)
archidektID = sys.argv[1]

### Set up logging
logging.basicConfig(filename='decklist.log', level=logging.INFO)
logging.info(f"Starting decklist build for Archidekt ID: {archidektID}")

### Check to see if the cache.db file exists, if not, create it
if not os.path.exists('cache.db'):
    db = sqlite3.connect('cache.db')
    db.execute('CREATE TABLE IF NOT EXISTS oracle_ids (card_id TEXT PRIMARY KEY, oracle_id TEXT, card_name TEXT)')
    db.close()

### Set up database connection; this will be used to cache results from the OracleID lookup
db = sqlite3.connect('cache.db')

### Pull CSV file into local memory, add OracleID and create Total Card Count
logging.info(f"Loading card library.")
cardLibrary = pd.read_csv('le.csv')

### Filter down to the pertinent columns needed
logging.info(f"Filtering columns.")
cardLibrary = cardLibrary.filter(['Name', 'CardID', 'Number of Non-foil', 'Number of Foil', 'ScryfallID']) 

### Add the foil and non-foil counts into a single column
logging.info(f"Consolidating counts.")
cardLibrary["Quantity"] = cardLibrary["Number of Non-foil"] + cardLibrary["Number of Foil"]

### Drop the foil/non-foil columns as they're unnecessary
logging.info(f"Dropping unnecessary columns.")
cardLibrary = cardLibrary.drop(columns=['Number of Non-foil', 'Number of Foil'])

### Grab the Oracle IDs for each card
logging.info(f"Adding Oracle IDs. This could take awhile.")
cardLibrary["OracleID"] = cardLibrary["ScryfallID"].apply(getOracleId)


## Report on the card library progress...
print(f"There were {str(cardLibrary.shape[0])} rows imported from the CSV.")

### Deduplicating the card library
print(f"Now deduplicating the card library.")
## Group by OracleID and sum the Quantity, then drop the dupes and reindex
cardLibrary["Quantity"] = cardLibrary.groupby(['OracleID'])['Quantity'].transform('sum')
cardLibrary = cardLibrary.drop_duplicates(subset=['OracleID']).reset_index()  

### Final report on the card library size
logging.info(f"There are now {str(cardLibrary.shape[0])} cards in the library.")

### Grab the Archidekt decklist
logging.info (f"Attempting to build a decklist for Archidekt ID: {archidektID}.")
jsondecklist = requests.get(f'https://archidekt.com/api/decks/{archidektID}/').json()
decklist = jsondecklist['cards']

### Create a new dataframe to hold the decklist 
shoppingList = []
haveList = []
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


### Print out the shopping list
print("SHOPPING LIST")
for item in shoppingList:
    print(f"{item[1]}x {item[0]}")

### Print out the have list
print("HAVE LIST")
for item in haveList:
    print(f"{item[1]}x {item[0]} (Have: {item[2]})")
