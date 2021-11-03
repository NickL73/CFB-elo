"""
Adapted from this blog post by Bill as CollegeFootballData: 
	https://blog.collegefootballdata.com/talking-tech-elo-ratings/
"""
import cfbd
import datetime
import pickle

# Get the current year and set first year
current_year = datetime.datetime.now().year
first_year = 1869 # As far back as CFBD goes

# configure API key
configuration = cfbd.Configuration()
configuration.api_key['Authorization'] = 'aZuW31mCep/CXE4KlX3ThSoyns/qaojw4QhRuIdSxJhdqV6hXzsuedaQRJVMyn+W'
configuration.api_key_prefix['Authorization'] = 'Bearer'

# instantiate a games API instance
api_config = cfbd.ApiClient(configuration)
games_api = cfbd.GamesApi(cfbd.ApiClient(configuration))	

# Define a sorting function for when we have all of the games
def date_sort(game):
    game_date = datetime.datetime.strptime(game['start_date'], "%Y-%m-%dT%H:%M:%S.000Z")
    return game_date

# Scrape all the college football games in the database until the most recent
games = []

for year in range(first_year, current_year + 1):
	response = games_api.get_games(year=year)
	games = [*games, *response]

games = [dict(
			start_date = g.start_date,
			home_team = g.home_team,
			home_conference = g.home_conference,
			home_points = g.home_points,
			away_team = g.away_team,
			away_conference = g.away_conference,
			away_points = g.away_points,
			neutral_site = g.neutral_site,
			season = g.season,
			season_type = g.season_type,
			week = g.week
			) for g in games if g.home_points is not None and g.away_points is not None]

# Sort the games sequentially
games.sort(key=date_sort)

# Write the scraped data to a file for easier access later
with open('data/all_games.pkl', 'wb') as file:
    pickle.dump(games, file)