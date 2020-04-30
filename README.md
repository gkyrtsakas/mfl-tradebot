# MFL Trade Bot

Scrape trades from MyFantasyLeague and post them to GroupMe.

## Dependencies
* Python 3.x
* requests **https://pypi.org/project/requests/** (install with command: pip3 install requests)

## Usage
**1.** Follow the instructions on MFL to create and register an API client.

**2.** Follow the instructions on GroupMe to create a Bot and add it to your desired chat. Take the Bot ID and put it in config.json.

**3.** Take your newly created user agent and put it in config.json.

**4.** Fill out the year and league ID fields in config.json where the league ID 
is the listed in your league's URL:

e.g. https://www.myfantasyleague.com/**_year_**/home/**_leagueID_**#0...

**5.** Create a cronjob to run *tradebot.py* once every 5 minutes.


## Contributing
Feel free to make it better and send pull requests. 

## License
See COPYING
