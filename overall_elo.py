import datetime
import pickle
import math

# Initial variables for the ELO system, partially taken from 538 NFL ELO
INITIAL_FBS = 1550.0 # the assigned starting Elo value for an FBS  team
INITIAL_FCS = 1200.0 # the assigned starting Elo for a non-FBS team
HFA = 65.0
K = 25.0 # the speed at which Elo ratings change
REVERT = 1/3 # Between seasons, a team retains 2/3 of its previous season's rating


# Load the game data
with open('data/all_games.pkl', 'rb') as file:
	games = pickle.load(file)

# A helper function for sorting the teams
def elo_sort(team):
	return team['elo']

# Perform the actual Elo rating

# Initialize team objects to maintain ratings
teams = {}
STARTING = 2021
last = 1869
for game in games:
	if game['season'] >= STARTING:
		# Assign initial ELO scores if the teams have not yet been seen
		if not game['home_team'] in teams:
			is_fbs = game['home_conference'] != None # the data only has conferences for FBS teams
			init_elo = (INITIAL_FCS if game['home_conference'] is None else INITIAL_FBS)
			teams[game['home_team']] = {
				'name': game['home_team'],
				'season': None,
				'elo': init_elo
			}

		if not game['away_team'] in teams:
			is_fbs = game['away_conference'] != None
			init_elo = (INITIAL_FCS if game['home_conference'] is None else INITIAL_FBS)
			teams[game['away_team']] = {
				'name': game['away_team'],
				'season': None,
				'elo': init_elo
			}

		# Grab the teams from the stored dict
		home_team = teams[game['home_team']]
		away_team = teams[game['away_team']]

		
		# Check if the beginning of a new season, and adjust the scores accordingly
		for team in [home_team, away_team]:
			if game['week'] == 1:
				#Multiply the previous year's ELO by the REVERT (repeat if multiple years since games)
				if team['season'] and game['season'] != team['season']:
					years_absent = game['season'] - team['season'] # how many years since last game
					for y in range(years_absent):
						team['elo'] = 1550*REVERT + team['elo']*(1-REVERT)

			#Reset the season
			team['season'] = game['season']

		# Calculate the difference in elo between the home and away teams
		elo_diff = home_team['elo'] - away_team['elo'] + (0 if game['neutral_site'] else HFA) # add home field advantage if applicable
		#print(game)
		# Calculate the forecasted probability by ELO score
		exp = -elo_diff / 400
		prob = 1 / (1 + 10**exp)

		# Margin of victory is used as a K multiplier
		point_difference = game['home_points'] - game['away_points']

		# Annotate who actually won the game
		result = 1.0 if point_difference > 0 else 0.0 if point_difference < 0 else 0.5 

		# Margin of value is going to be used a K multiplieer (fivethirtyeight)
		mult = math.log(max(abs(point_difference), 1) + 1.0) * (2.2 / (1.0 if result == 0.5 else ((elo_diff if result == 1.0 else -elo_diff) * 0.001 + 2.2)))

		# Calculate the points won or lost
		shift = (K * mult) * (result - prob)

		# Apply shift
		home_team['elo'] += shift
		away_team['elo'] -= shift

		if game['season'] > last:
			last = game['season']


def elo_sort(team):
    return team['elo']

#### Print out the results
end_elos = [dict(team=key, elo=teams[key]['elo']) for key in teams if teams[key]['season'] == last]
end_elos.sort(key=elo_sort, reverse=True)

"""
for e in range(len(end_elos)):
	if end_elos[e]['year'] != last:
		del end_elos[e]
"""

for t in range(50):
  print("{0:>3}. {1:>20} - {2:<12}".format(t+1, end_elos[t]['team'], end_elos[t]['elo']))
