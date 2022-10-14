# to_csv.py reads all card .json's and produces (stdout) one big tab-separated 
# csv file with all card info.
# Usage: python3 to_csv.py >csv/all_cards.csv
# *  Linebreaks converted to \\n
# *  Confusion may arise in certain csv readers if there is a quote mismatch. 
#    Writing to stderr if a field contains an odd number of quote characters.
#    Mitigation is to adjust the card data.
# *  linked_card represented just like any other card
import json
import os
import sys

def load_json_file(path):
    with open(path, "r") as f: return json.loads(f.read())

# load_cards returns the cards defined in a json file
# Returns None if file doesn't exist
def load_cards(fmt, pack, sets):
    PACK_FOLDER = "pack"
    path = os.path.join(PACK_FOLDER, fmt.format(pack["code"]))
    if os.path.isfile(path):
        cards = load_json_file(path)
        for c in cards:
            c["pack_name"] = pack["name"]
            if "set_code" in c:
                c["set_name"] = sets[c["set_code"]]["name"]
        return cards

# get_all_cards returns all card info in the .json files as one array
def get_all_cards():
    sets = {}
    for s in load_json_file("sets.json"):
        sets[s["code"]] = s

    all_cards = []
    for p in load_json_file("packs.json"):
        c = load_cards("{}.json", p, sets)
        if c: all_cards += c
        c = load_cards("{}_encounter.json", p, sets)
        if c: all_cards += c
    return  all_cards

# add_card adds the card to the cards_out dictionary and
# all relevant fields to the fields set.
def add_card(card, cards_out, fields):
    c = {}
    for f in card.keys():
        # skip dictionaries. linked_card handled separately
        if not type(card[f]) is dict:
            fields.add(f)
            c[f]=str(card[f]).replace('\n', '\\n')
    cards_out[c["code"]] = c

# eprint prints to stderr
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def main():
    fields = set()
    cards_out = {}
    for card in get_all_cards():
        add_card(card, cards_out, fields)
        if "linked_card" in card:
            add_card(card["linked_card"], cards_out, fields)

    # Resolve duplicates by making the duplicate a copy of its original    
    for code in cards_out:
        c = cards_out[code]
        if "duplicate_of" in c:
            cards_out[code] = cards_out[c["duplicate_of"]].copy()
            for f in c:
                cards_out[code][f]=c[f]

    # sort the fields alphabetically to ensure deterministic output
    fields = sorted(fields)
    print("\t".join(fields))
    for code in cards_out:
        c = cards_out[code]
        csv_line = []
        for f in fields:
            if f in c:
                # Odd number of quote characters?
                if c[f].count('"') %2 != 0:
                    eprint("Card code:", c["code"],"field:",f, "quote characters:", c[f].count('"'), "\n",c[f])
            csv_line.append(c[f] if f in c else "")
        print("\t".join(csv_line))

main()
