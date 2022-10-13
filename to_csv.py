# to_csv.py reads all card .json's and produces (stdout) one big tab-separated csv file will all card info.
# *  Linebreaks converted to \n
# *  Confusion may arise in certain csv readers if there is a quote mismatch, writing to stderr if
#    a field contains an odd number of quote characters. Mitigation is to adjust the card data.
# *  linked_card represented just like any other card
import json
import os
import sys

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

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
            c["pack_name"] = p["name"]
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

# add_card appends the card to the cards_out array and
# all relevant fields to thefields set.
def add_card(card, cards_out, fields):
    c = {}
    for f in card.keys():
        # skip dictionaries. linked_card handled separately
        if not type(card[f]) is dict:
            fields.add(f)
            c[f]=str(card[f]).replace('\n', '\\n')
    cards_out.append(c)

def main():
    fields = set()
    cards_out = []
    for card in get_all_cards():
        add_card(card, cards_out, fields)
        if "linked_card" in card:
            add_card(card["linked_card"], cards_out, fields)

    # sort the fields alphabetically to ensure consistent/deterministic output
    fields = sorted(fields)
    print("\t".join(fields))
    for c in cards_out:
        csv_line = []
        for f in fields:
            if f in c:
                # Odd number of quote characters?
                if c[f].count('"') %2 != 0:
                    eprint("Card code:", c["code"],"field:",f, "quote characters:", c[f].count('"'), "\n",c[f])
            csv_line.append(c[f] if f in c else "")
        print("\t".join(csv_line))

main()