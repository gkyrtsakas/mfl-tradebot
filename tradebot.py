import requests
import json
import re
import time
import discord
import asyncio
import os

base_url = "https://api.myfantasyleague.com/"

franchises_dict_g = {}
players_dict_g = {}
timestamp_g = 0
league_id_g = ""
groupme_bot_id_g = ""
year_g = ""
mfl_user_agent_g = ""
discord_key_g = ""
discord_channel_g = ""
chat_api_list_g = []
rosters_json_g = None

def get_os_env_var(env_var):
    return os.environ.get(env_var)


def current_unix_timestamp():
    return int(time.time())

def remove_html_from_string(s):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', s)

def https_request(url):
    headers = {
        'User-Agent': mfl_user_agent_g
    }

    resp = requests.get(url, headers=headers)
    return resp.text

def get_rosters():
    global rosters_json_g
    s = base_url + year_g + "/export?TYPE=rosters&L=" + league_id_g + "&JSON=1"
    rosters_json_g = json.loads(https_request(s))


def get_trades():
    s = base_url + year_g + "/export?TYPE=transactions&TRANS_TYPE=TRADE&DAYS=7&L=" + league_id_g + "&JSON=1"
    trades_json = https_request(s)
    return trades_json

def get_league():
    s = base_url + year_g + "/export?TYPE=league&L=" + league_id_g + "&JSON=1"
    league_json_string = https_request(s)
    league_json = json.loads(league_json_string)
    franchises = (league_json["league"]["franchises"]["franchise"])
    for franchise in franchises:
        franchises_dict_g[franchise["id"]] = remove_html_from_string(franchise["name"])


def get_players_from_MFL():
    s = base_url + year_g + "/export?TYPE=players&L=" + league_id_g + "&JSON=1"
    players_json_string = https_request(s)
    players_json = json.loads(players_json_string)
    players = players_json["players"]["player"]
    for player in players:
        players_dict_g[player["id"]] = player

    players_dict_g["timestamp"] = str(current_unix_timestamp())
    
    with open('players.json', 'w') as f:
        f.write(json.dumps(players_dict_g))

def get_players():
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

    print("MFL Players DB last updated:")
    print(time.strftime("%d %b %Y %H:%M:%S %z", time.localtime(int(players_dict_g["timestamp"]))))
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

def round_to_dollar(amt):
    return str(int(round(float(amt), 0)))

def get_player_contract_details(player):
    franchises = rosters_json_g["rosters"]["franchise"]
    for franchise in franchises:
        for roster_player in franchise["player"]:
            if roster_player["id"] == player["id"]:
                return "($" + round_to_dollar(roster_player["salary"]) + ", " + roster_player["contractYear"] + "yr)\n"
    return "\n"


def parse_player(asset):
    player = players_dict_g[asset]
    print(player)
    s = u'\u00b7' + " " + player["name"] + " " + player["team"] + " " + player["position"] + " "
    s += get_player_contract_details(player)
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

def franchise_parser(franchise):
    return "**" + franchises_dict_g[franchise] + "**"

def update_timestamp(new_ts):
    global timestamp_g
    timestamp_g = new_ts
    with open("timestamp", "w") as f:
        f.write(str(timestamp_g))

def load_timestamp():
    global timestamp_g
    try:
        with open("timestamp", "r") as f:
            s = f.read()
            timestamp_g = int(s)
    except:
        print("No timestamp file...")

def trade_parser(trade):
    ts_int = int(trade["timestamp"])
    if ts_int > timestamp_g:
        update_timestamp(ts_int)
    else:
        #Trade already processed
        print("trade already processed")
        return None

    s = ""

    s += franchise_parser(trade["franchise"]) + " trades:\n"
    s += trade_asset_parser(trade["franchise1_gave_up"])

    s += franchise_parser(trade["franchise2"]) + " trades:\n"
    s += trade_asset_parser(trade["franchise2_gave_up"])
    return s

def process_trades(trades_json_string):
    transactions_json = json.loads(trades_json_string)
    if len(transactions_json["transactions"]) == 0:
        return # no trades to process
    transactions = transactions_json["transactions"]["transaction"]

    if isinstance(transactions, dict):
        ret = trade_parser(transactions)
        if ret:
            print("API Call(s)")
            call_APIs(ret)
    elif isinstance(transactions, list):
        transactions.reverse()
        for trade in transactions:
            ret = trade_parser(trade)
            if ret:
                print("API Call(s)")
                call_APIs(ret)

def groupme_API_post_message(message):
    url = "https://api.groupme.com/v3/bots/post"
    data = {
        "text": message,
        "bot_id": groupme_bot_id_g
    }
    resp = requests.post(url, json=data)
    print(resp.text)

def discord_API_post_message(message):
    asyncio.set_event_loop(asyncio.new_event_loop())
    client = discord.Client()
    formatted_message = "-------------------------------------------\n" + message + "-------------------------------------------\n"

    @client.event
    async def on_ready():
        print(f'{client.user} has connected to Discord!')
        guild = client.guilds[0]
        for channel in guild.channels:
            if channel.name == discord_channel_g:
                await channel.send(content=formatted_message)
                await client.close()

    client.run(discord_key_g)

def call_APIs(message):
    if "discord" in chat_api_list_g:
        discord_API_post_message(message)
    if "groupme" in chat_api_list_g:
        groupme_API_post_message(message)

def load_config():
    global league_id_g
    global groupme_bot_id_g
    global year_g
    global mfl_user_agent_g
    global discord_key_g
    global discord_channel_g
    global chat_api_list_g

    config_file = "config.json"
    loaded_from_file = True

    with open(config_file, "r") as f:
        config = json.load(f)
        league_id_g = config["league_id"]
        groupme_bot_id_g = config["groupme_bot_id"]
        year_g = config["year"]
        mfl_user_agent_g = config["mfl_user_agent"]
        discord_key_g = config["discord_key"]
        discord_channel_g = config["discord_channel"]
    
    if not league_id_g or not year_g or not mfl_user_agent_g:
        loaded_from_file = False
        league_id_g = get_os_env_var("TB_LID")
        groupme_bot_id_g = get_os_env_var("TB_GRPME_BID")
        year_g = get_os_env_var("TB_YEAR")
        mfl_user_agent_g = get_os_env_var("TB_MFL_UA")
        discord_key_g = get_os_env_var("TB_DISC_KEY")
        discord_channel_g = get_os_env_var("TB_DISC_CHAN")

    if not league_id_g or not year_g or not mfl_user_agent_g:
        print("config.json/environment missing mfl league information")
    
    if groupme_bot_id_g:
        chat_api_list_g.append("groupme")

    if discord_key_g and discord_channel_g:
        chat_api_list_g.append("discord")

    if not chat_api_list_g:
        print("No chat clients provided (groupme/discord) in config.json... exiting")
        return False
    else:
        if loaded_from_file:
            print("Loaded config from " + config_file + "")
        else:
            print("Loaded config from environment")
        return True

def main():
    if load_config():
        load_timestamp()
        get_rosters()
        get_league()
        get_players()
        process_trades(get_trades())
    else:
        print("Incorrect config.json options")


if __name__ == "__main__":
    main()