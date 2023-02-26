# Kingdomino

Fully Implemented in Python 3.6+ including:
* Typing
* Valid play finder and santisation
* Colored terminal play
* Bonus rules
* Constant time scorer from abstract object based Union Find

More here http://www.blueorangegames.eu/pf/kingdomino/

## Instructions
1. `python3.6 -m pip install colored --user`
2. `python3.6 game.py`
3. `python3.6 game.py filename.txt` For saving terminal inputs

## TODO
* Refactor to simplify
* Add rule checking
* Double check that the input is within the 5x5 grid?
* Refactor `Play`'s `__eq__` function
* Refactor `Line`'s `choose` function
