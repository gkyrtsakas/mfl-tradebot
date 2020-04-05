import requests
import json

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

def trade_print(trade):
    # print(trade)
    print("TRADE")
    print("%s gave up %s" % (trade["franchise"], trade["franchise1_gave_up"]))
    print("%s gave up %s" % (trade["franchise2"], trade["franchise2_gave_up"]))
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
    # get_rosters()
    process_trades(get_trades())


if __name__ == "__main__":
    main()