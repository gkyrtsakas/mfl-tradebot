# MFL Trade Bot


Scrape trades from MyFantasyLeague and post them to GroupMe.

### Usage
I probably should have made this more user-friendly, but with most things, I design them on the fly.

**NOTE:** This is designed and tested on Ubuntu 16.04 with Python 2.7 and cURL. I make no guarantees it works anywhere else. Actually I make no guarantees that it works at all for your league.

**1.** Adjust the *getplayers.sh* and *run.sh* scripts so they contain the url of your league. You will also need to adjust the directories that the xml files are downloaded to.

**2.** Edit *tradebot.py* to contain your GroupMe Bot ID in the variable "GROUPME_BOTID"

**3.** Create a cronjob to run the *getplayers.sh* script once a day (MFL updates their player base once a day).

**4.** Create a cronjob to run the *run.sh* script once every 5 minutes.


## Contributing
Feel free to make it better and send pull requests. 

## License
See COPYING

## FAQ
Will you add *blah* feature? No, probably not.