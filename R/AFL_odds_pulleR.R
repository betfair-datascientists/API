###################################################
### AFL Model
### Betfair API Odds GrabbR
###
### This script allows you to access the Betfair
### API and retrive exchange odds for all the 
### matches for the upcoming round of AFL games
###################################################

## Loading required packages
library(tidyverse) ## package for general data manipulation - https://www.tidyverse.org/
library(abettor) ## wrapper package for the Betfair API - https://github.com/phillc73/abettor

## Login to Betfair - should return "SUCCESS:" on successful login
betfair_login <- abettor::loginBF(username = 'your_username',
                                  password = 'your_password',
                                  applicationKey = "your_betfair_app_key")

###################################################
## Retrieving all AFL competitions for 
## which markets are currently alive
## on the Betfair Exchange
###################################################

all_afl_markets <- abettor::listCompetitions(
  eventTypeIds = 61420,  ## AFL is eventTypeId 61420,
  toDate = (format(Sys.time() + 86400 * 180, "%Y-%m-%dT%TZ")) ## Look ahead until the next 180 days
)
###################################################
## Retrieving the competition id
## for the regular AFL season
###################################################

afl_competition_id <- all_afl_markets %>%
  dplyr::pull(competition) %>% ## Extracting the variable competition which is a nested data frame
  dplyr::filter(name == "AFL") %>% ## Filtering for the competition we need
  dplyr::pull(id) ## Extracting the id for the competition we need

###################################################
## Obtaining all markets that are currently 
## alive on the Betfair Exchange that belong to
## Competition ID that is mapped to the AFL
###################################################

all_afl_markets <- abettor::listMarketCatalogue(
  eventTypeIds = 61420, ## AFL is eventTypeId 61420
  marketTypeCodes = "MATCH_ODDS", ## Restrict our search to Match Odds only, not other markets for the same match
  competitionIds = afl_competition_id, ## Restrict our search to AFL Matches Only
  toDate = (format(Sys.time() + 86400 * 60, "%Y-%m-%dT%TZ")) ## Look ahead until the next 60 days
)

###################################################
## Obtaining the current odds on the Betfair
## Exchange for all the markets that were 
## obtained in the previous step
###################################################

## Creating a vector/array of all market ids
all_afl_markets_market_ids <- all_afl_markets %>%
  pull(marketId)

## This function takes in a single market id and returns 
## the current live odds on the Betfair Exchange for that market
fetch_odds <- function(market_id) {
  
  ## Retrieving market odds for a single market
  odds <- abettor::listMarketBook(marketIds = market_id, ##Runs listMarketBook for given market_id
                                  priceData = "EX_BEST_OFFERS" ##Fetching the top 3 odds, EX_ALL_OFFERS fetches the entire depth of prices
  ) %>%
    pull(runners) %>% ## Extracting the runners field which has details of odds
    as.data.frame() %>% ## Converting to data frame from list
    select(lastPriceTraded) %>% ## Extracting team and last matched odds
    mutate(market_id = market_id) %>% ## Padding market id to the data to make it unique to this match
    bind_cols(data.frame(outcome = c("o_1","o_2"))) %>% ## Creating outcome order to maintain consistency
    spread(outcome, lastPriceTraded) %>% ## Reshaping data to make it 1 row per match
    rename(team_1_odds = o_1,
           team_2_odds = o_2) %>% ##Renaming columns such that all matches can be combined into one data frame
    select(market_id, team_1_odds, team_2_odds) ## Ordering columns in the right order
  
  return(odds)
}

## The code below maps (or loops) each market id in the vector we created
## above through the fetch_odds function and retrives the market odds 
## into a single data frame
afl_market_odds <- map_dfr(.x = all_afl_markets_market_ids, ##Iterate over market ids
                                .f = fetch_odds ## through function fetch_odds
) %>%
  bind_cols(all_afl_markets %>% ## Merge with event names to identify which match odds it is
              pull(event) %>%
              select(name)) %>% 
  mutate(team_1 = gsub(" v .*","",name), ## Extracting team 1 from match name
         team_2 = gsub(".* v ", "", name)) %>% ## Extracing team 2 from match name
  select(team_1, team_2, team_1_odds, team_2_odds) ## Extracting columns that we need

## Writing output to csv file
write_csv(afl_market_odds, "weekly_afl_odds.csv")