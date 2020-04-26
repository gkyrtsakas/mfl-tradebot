import requests
import json
import re
import time

franchises_dict_g = {}
players_dict_g = {}

def current_unix_timestamp():
    return int(time.time())

def remove_html_from_string(s):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', s)

def https_request(url):
    headers = {
        'User-Agent': 'Tradebot_User_Agent'
    }

    resp = requests.get(url, headers=headers)

    return resp.text

def get_rosters():
    s = "https://www61.myfantasyleague.com/2020/export?TYPE=rosters&L=14095&JSON=1"

    rosters_json = json.loads(https_request(s))

    # print(rosters_json["encoding"])

    pretty_text = json.dumps(rosters_json, indent=4, sort_keys=True)

    # print(resp.text)

    with open("rosters.json", "w") as text_file:
        text_file.write(pretty_text)


def get_trades():
    s = "https://www61.myfantasyleague.com/2020/export?TYPE=transactions&TRANS_TYPE=TRADE&L=14095&JSON=1"

    trades_json = https_request(s)
    return trades_json

def get_league():
    s = "https://www61.myfantasyleague.com/2020/export?TYPE=league&L=14095&JSON=1"

    league_json_string = https_request(s)
    league_json = json.loads(league_json_string)

    franchises = (league_json["league"]["franchises"]["franchise"])

    for franchise in franchises:
        franchises_dict_g[franchise["id"]] = remove_html_from_string(franchise["name"])

    # print(franchises_dict_g)

def get_players_from_MFL():
    s = "https://www61.myfantasyleague.com/2020/export?TYPE=players&L=14095&JSON=1"

    players_json_string = https_request(s)
    players_json = json.loads(players_json_string)

    players = players_json["players"]["player"]

    for player in players:
        players_dict_g[player["id"]] = player

    players_dict_g["timestamp"] = str(current_unix_timestamp())
    
    with open('players.json', 'w') as f:
        f.write(json.dumps(players_dict_g))

def get_players():
    # {
    #     "position": "TMWR",
    #     "name": "Bills, Buffalo",
    #     "id": "0151",
    #     "team": "BUF"
    # }
    # This should be scheduled to run once or twice every day

    # Attempt to load from disk before making API call
    global players_dict_g
    if not players_dict_g:
        try:
            with open('players.json', 'r') as f:
                players_dict_g = json.load(f)
                print("Loaded players file")
        except:
            print("No players file: retrieving from MFL")

    if not players_dict_g:
        get_players_from_MFL()
        return

    print(players_dict_g["timestamp"])
    if int(players_dict_g["timestamp"]) + 86400 < current_unix_timestamp():
        print("Players file is stale, updating from MFL")
        get_players_from_MFL()
    

def parse_future_pick(asset):
    asset_split = asset.split("_")
    s = u'\u00b7' + " " + asset_split[2] + " " + asset_split[3]
    if asset_split[3] == "1":
        s += "st"
    elif asset_split[3] == "2":
        s += "nd"
    elif asset_split[3] == "3":
        s += "rd"
    else:
        s += "th"

    s += "\n"    
    return s
    
def parse_draft_pick(asset):
    asset_split = asset.split("_")
    rd = int(asset_split[1]) + 1
    pick = int(asset_split[2]) + 1
    s = u'\u00b7' + " " + str(rd) + "." + str(pick).zfill(2) + "\n"
    return s

def parse_player(asset):
    player = players_dict_g[asset]
    s = u'\u00b7' + " " + player["name"] + " " + player["team"] + " " + player["position"] + "\n"
    return s

def trade_asset_parser(assets):
    s = ""
    for asset in assets.split(","):
        if asset == "":
            continue
        if asset[0] == "F":
            s += parse_future_pick(asset)
        elif asset[0] == "D":
            s += parse_draft_pick(asset)
        else:
            s += parse_player(asset)
    return s

def trade_print(trade):
    # print(trade)
    print("TRADE")
    print("%s gave up %s" % (trade["franchise"], trade["franchise1_gave_up"]))
    print(trade_asset_parser(trade["franchise1_gave_up"]))
    print("%s gave up %s" % (trade["franchise2"], trade["franchise2_gave_up"]))
    print(trade_asset_parser(trade["franchise2_gave_up"]))
    print("")

def process_trades(trades_json_string):
    trades_json = json.loads(trades_json_string)
    trades = trades_json["transactions"]
    # print(trades)
    if (len(trades["transaction"]) == 1):
        trade_print(trades["transaction"])
    else:
        print("hi mom")
        print(trades["transaction"])
        for trade in trades["transaction"]:
            trade_print(trade)
            



def main():
    get_rosters()
    get_league()
    get_players()
    process_trades(get_trades())

    # print(players_dict_g)

if __name__ == "__main__":
    main()