# Betfair API Tutorials in R
Betfair's API can be easily traversed in R. It allows you to retrieve market information, create/cancel bets and manage your account. This folder will have a collection of easy to follow API tutorials in R.

## Required Packages
Two R packages are required.
```
library(tidyverse)
library(abettor)
```

The abettor package can be downloaded [here](https://github.com/phillc73/abettor). For an in-depth understanding of the package, have a read of the documentation. Instructions are also provided in the sample code.

## Get World Cup Odds Tutorial
This tutorial walks you through the process of retrieving exchange odds for all the matches from the upcoming FIFA World Cup 2018. This can be modified for other sports and uses.

## Login to Betfair
To login to betfair, replace the following dummy username, password and app key with your own.
```
abettor::loginBF(username = "betfair_username",
                 password = "betfair_password",
                 applicationKey = "betfair_app_key")
```

## Finding Event IDs
In order to find data for specific markets, you will first need to know the event ID. This is easily achieved with the abettor package. To find the event IDs of events in the next 60 days:
```
abettor::listEventTypes(toDate = (format(Sys.time() + 86400 * 60, "%Y-%m-%dT%TZ")))
```

This will return the following structured DataFrame:

  | eventType.id |  eventType.name |marketCount
  | ------------ | --------------- | ----------
1 |            1 |          Soccer |       1193
2 |            2 |          Tennis |       2184
3 |         7522 |      Basketball |          1
5 |            4 |         Cricket |         37
7 |            7 |    Horse Racing |        509
10|        61420 |Australian Rules |         31
11|         4339 |Greyhound Racing |        527

## Finding Competition IDs
Once you have the event ID, the next logical step is to find the competition IDs for the event you want to get data for. For example, if you want to find the competition IDs for Australian Rules, you would use the following
```
abettor::listCompetitions(
  eventTypeIds = 61420,  ## AFL is eventTypeId 61420,
  toDate = (format(Sys.time() + 86400 * 180, "%Y-%m-%dT%TZ")) ## Look ahead until the next 180 days
)
```
This will return the following structured DataFrame:
| competition.id |   competition.name | marketCount | competitionRegion
| - | - | -| -
| 11516633 |Brownlow Medal 2018  | 3 | AUS
| 11897406 | AFL | 78 | AUS

## Finding Specific Markets
The next logical step is to find the market that you are interested in. Furthering our example above, if you want the Match Odds for all Australian Rules games over the next 60 days, simply use the Competition ID from above in the following.
```
abettor::listMarketCatalogue(
  eventTypeIds = 61420,
  marketTypeCodes = "MATCH_ODDS", ## Restrict our search to Match Odds only, not other markets for the same match
  competitionIds = 11897406,
  toDate = (format(Sys.time() + 86400 * 60, "%Y-%m-%dT%TZ"))
```

This returns a large DataFrame object with each market, participants and associated odds.

For more information and a more detailed walk through example, please read through our guides.