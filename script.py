import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from unidecode import unidecode

# URLs for five different leagues
leagues = {
    "La Liga": "https://www.transfermarkt.us/laliga/marktwerteverein/wettbewerb/ES1/plus/?stichtag=2023-08-15",
    "Premier League": "https://www.transfermarkt.us/premier-league/marktwerteverein/wettbewerb/GB1/plus/?stichtag=2023-08-15",
    "Serie A": "https://www.transfermarkt.us/serie-a/marktwerteverein/wettbewerb/IT1/plus/?stichtag=2023-08-15",
    "Bundesliga": "https://www.transfermarkt.us/bundesliga/marktwerteverein/wettbewerb/L1/plus/?stichtag=2023-08-15",
    "Ligue 1": "https://www.transfermarkt.us/ligue-1/marktwerteverein/wettbewerb/FR1/plus/?stichtag=2023-08-15"
}

headers = {'User-Agent': 'Mozilla/5.0'}

# Empty list to hold all the players' data
all_players_data = []

# Loop through each league
for league_name, url in leagues.items():
    print(f"Processing data for {league_name}...")

    try:
        # Send request to the league's URL
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Check if the request was successful
        response.encoding = 'utf-8'
    except requests.RequestException as e:
        print(f"Error fetching data for {league_name}: {e}")
        continue

    soup = BeautifulSoup(response.content.decode('utf-8', 'ignore'), 'html.parser')

    # Find the table
    table = soup.find('table', {'class': 'items'})
    if not table:
        print(f"Error: Table not found for {league_name}")
        continue

    # Get all rows except the first two (header rows)
    rows = table.find_all('tr')[2:]

    # Extract data from each row
    for row in rows:
        cols = row.find_all('td')
        if len(cols) < 6:
            continue

        # Extract Number, Team Name, League, Market Value, and % Change
        number = unidecode(cols[0].text.strip()) if cols[0].text.strip() else 'N/A'
        team_name = unidecode(cols[2].find('a').text.strip()) if cols[2].find('a') else 'N/A'
        old_market_value = unidecode(cols[4].text.strip()) if cols[4].text.strip() else 'N/A'
        new_market_value = unidecode(cols[5].text.strip()) if cols[5].text.strip() else 'N/A'
        percent_change = unidecode(cols[6].text.strip()) if cols[6].text.strip() else 'N/A'

        # Clean up market values
        if old_market_value.startswith('€'):
            old_market_value = old_market_value.replace('€', '').replace('m', ' Million').replace('k', ' Thousand')
        if new_market_value.startswith('€'):
            new_market_value = new_market_value.replace('€', '').replace('m', ' Million').replace('k', ' Thousand')

        # Append data for the player
        all_players_data.append({
            '#': number,
            'Team Name': team_name,
            'League': league_name,
            'Market Value (15 Aug 2023)': old_market_value,
            'Market Value (Now)': new_market_value,
            '% Change': percent_change
        })

    # Pause for 2 seconds to avoid overwhelming the server
    print(f"Finished processing {league_name}. Sleeping for 2 seconds...")
    time.sleep(2)

# Convert all the player data to a DataFrame
df = pd.DataFrame(all_players_data)

# Save the combined data to a CSV file
df.to_csv('top_5_leagues_market_value', index=False, encoding='utf-8')
print("Data saved to top_5_leagues_market_value")
