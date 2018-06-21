# Betfair API Tutorials in R
Betfair's API can be easily traversed in R. It allows you to retrieve market information, create/cancel bets and manage your account.

## Required Packages
Two R packages are required.
```
library(tidyverse)
library(abettor)
```

The abettor package can be downloaded [here](https://github.com/phillc73/abettor). For an in-depth understanding of the package, have a read of the documentation. Instructions are also provided in the sample code.

## Get World Cup Odds Tutorial
This tutorial walks you through the process of retrieving exchange odds for all the matches from the upcoming FIFA World Cup 2018. This can be modified for other sports and uses.