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

print(getOracleId('396f9198-67b6-45d8-91b4-dc853bff9623'))
print(getCardName('396f9198-67b6-45d8-91b4-dc853bff9623'))