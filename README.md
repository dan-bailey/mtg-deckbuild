# mtg-deckbuild
Script that takes your Magic the Gathering card list from [Lion's Eye](https://lionseyeapp.com/) in CSV and checks it against [Archidekt](https://archidekt.com) to show you what decks you can build with your library.  Uses Scryfall, and a Lion's Eye export file.

## howto
Export the Extended CSV from Lion's Eye and drop it into the same folder as this script, with the filename `le.csv`.

## usage
`python script.py <archidektID>`

## to-do list
* clean up reporting
* cache OracleIDs locally so I don't need to re-pull via API every time
* get card prices from Card Kingdom and TCGPlayer to determine rough prices for building a deck (also locally cached)
* ...
* PROFIT!!!
