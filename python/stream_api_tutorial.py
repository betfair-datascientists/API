# Import libraries
import betfairlightweight
import pandas as pd
import queue
import datetime

# This tutorial is based off the betfairlightweight stream tutorials
# which are available at
# https://github.com/liampauling/betfair/blob/master/examples/examplestreaming.py


# Change this certs path to wherever you're storing your certificates
certs_path = "your_certs_path"

# Change these login details to your own
username = "your_username"
pw = "your_password"
app_key = "your_app_key"

# Log in - if you have set up your certs use this
print("Logging in")
trading = betfairlightweight.APIClient(username, pw, app_key=app_key, certs=certs_path)
trading.login()

# Log in - if you haven't set up your certs use this
# trading = betfairlightweight.APIClient(username, pw, app_key=app_key)
# trading.login_interactive()


# create queue
output_queue = queue.Queue()

# create stream listener
print('Creating listener')
listener = betfairlightweight.StreamListener(
    output_queue=output_queue,
)

# create stream
print('Creating stream')
stream = trading.streaming.create_stream(
    listener=listener,
)

# Define a market filter
thoroughbreds_event_filter = betfairlightweight.filters.market_filter(
    event_type_ids=['7'], # Thoroughbreds event type id is 7
    market_countries=['AU'],
    market_start_time={
        'to': (datetime.datetime.utcnow() + datetime.timedelta(days=1)).strftime("%Y-%m-%dT%TZ")
    }
)

# Get a list of all thoroughbred events as objects
print("Getting future events")
aus_thoroughbred_events = trading.betting.list_events(
    filter=thoroughbreds_event_filter
)

# Create a DataFrame with all the events by iterating over each event object
aus_thoroughbred_events_today = pd.DataFrame({
    'Event Name': [event_object.event.name for event_object in aus_thoroughbred_events],
    'Event ID': [event_object.event.id for event_object in aus_thoroughbred_events],
    'Event Venue': [event_object.event.venue for event_object in aus_thoroughbred_events],
    'Country Code': [event_object.event.country_code for event_object in aus_thoroughbred_events],
    'Time Zone': [event_object.event.time_zone for event_object in aus_thoroughbred_events],
    'Open Date': [event_object.event.open_date for event_object in aus_thoroughbred_events],
    'Market Count': [event_object.market_count for event_object in aus_thoroughbred_events],
    'Local Open Date': [event_object.event.open_date.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None) 
                        for event_object in aus_thoroughbred_events]
})


# Get the first event's event ID
first_event_id = aus_thoroughbred_events_today.iloc[0]['Event ID']

market_catalogue_filter = betfairlightweight.filters.market_filter(event_ids=[first_event_id])

print("Getting a market id to listen to")
market_catalogues = trading.betting.list_market_catalogue(
    filter=market_catalogue_filter,
    max_results='100',
    sort='FIRST_TO_START',
)

# Create a DataFrame for each market catalogue
markets = pd.DataFrame({
    'Market Name': [market_cat_object.market_name for market_cat_object in market_catalogues],
    'Market ID': [market_cat_object.market_id for market_cat_object in market_catalogues],
    'Total Matched': [market_cat_object.total_matched for market_cat_object in market_catalogues],
})

# Get the market id
market_id = markets.loc[markets['Market Name'].str.contains('R'), 'Market ID'].values[0]

# Subscribe to markets
# Create Filters

market_filter = betfairlightweight.filters.streaming_market_filter(
    event_type_ids=['7'],
    country_codes=['AU'],
    market_types=['WIN'],
    market_ids=[market_id]  # Add the market ID we found above to the filter.
)

market_data_filter = betfairlightweight.filters.streaming_market_data_filter(
    fields=['EX_BEST_OFFERS', 'EX_MARKET_DEF'],
    ladder_levels=3,
)

# Subscribe
streaming_unique_id = stream.subscribe_to_markets(
    market_filter=market_filter,
    market_data_filter=market_data_filter,
    conflate_ms=1000,  # send update every 1000ms
    initial_clk=listener.initial_clk, # These allow for recovery if you disconnect
    clk=listener.clk
)

# Start stream
stream.start(_async=True)

print(f"Print streaming updates for market {market_id}")
# Print stream updates
while True:
    # Get the market books at the front of the queue
    print("Getting market books")
    market_books = output_queue.get()
    print(market_books)
    # Iterate over the market books and print updates, times etc.
    for market_book in market_books:
        print("This is the market book object:", market_book, "\n")
        print("This is the time of update:", market_book.publish_time, "\n")
        print("This is the actual streaming updated data:", market_book.streaming_update)

trading.logout()
