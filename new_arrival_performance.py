import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from unidecode import unidecode

# URLs for five different leagues
leagues = {
    "La Liga": "https://www.transfermarkt.us/laliga/neuzugaenge/wettbewerb/ES1/saison_id/2024/transferzeitpunkt//spieltag//plus/1",
    "Premier League": "https://www.transfermarkt.us/premier-league/neuzugaenge/wettbewerb/GB1/saison_id/2024/transferzeitpunkt//spieltag//plus/1",
    "Serie A": "https://www.transfermarkt.us/serie-a/neuzugaenge/wettbewerb/IT1/saison_id/2024/transferzeitpunkt//spieltag//plus/1",
    "Bundesliga": "https://www.transfermarkt.us/bundesliga/neuzugaenge/wettbewerb/L1/saison_id/2024/transferzeitpunkt//spieltag//plus/1",
    "Ligue 1": "https://www.transfermarkt.us/ligue-1/neuzugaenge/wettbewerb/FR1/saison_id/2024/transferzeitpunkt//spieltag//plus/1"
}

headers = {'User-Agent': 'Mozilla/5.0'}

# Empty list to hold all the players' data
all_players_data = []

# Maximum number of pages to check for each league
max_pages = 10

# Loop through each league
for league_name, base_url in leagues.items():
    print(f"Processing data for {league_name}...")

    # Loop through the pages (up to max_pages)
    for page in range(1, max_pages + 1):
        # Construct the URL for the current page
        if page == 1:
            url = base_url  # For the first page, use the base URL
        else:
            url = f"{base_url}/ajax/yw1/saison_id/2024/transferzeitpunkt//spieltag//plus/1/page/{page}"

        try:
            # Send request to the page URL
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Check if the request was successful
            response.encoding = 'utf-8'
        except requests.RequestException as e:
            print(f"Error fetching data for {league_name}, page {page}: {e}")
            break  # Stop if the page doesn't exist or there's a request error

        soup = BeautifulSoup(response.content.decode('utf-8', 'ignore'), 'html.parser')

        # Find the table
        table = soup.find('table', {'class': 'items'})
        if not table:
            print(f"Error: Table not found for {league_name} on page {page}")
            continue

        # Get all rows except the first two (header rows)
        rows = table.find_all('tr')[2:]

        # Extract data from each row
        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 6:
                continue

            # Extract Number, Team Name, League, Market Value, and % Change
            name_tag = cols[0].find('img')
            name = unidecode(name_tag['title'] if name_tag else 'N/A')
            position = unidecode(cols[3].text.strip()) if cols[3].text.strip() else 'N/A'
            club_tag = cols[4].find('img')
            Club = unidecode(club_tag['title'] if club_tag else 'N/A')
            new_market_value = unidecode(cols[6].text.strip()) if cols[6].text.strip() else 'N/A'
            goals_scored = unidecode(cols[7].text.strip()) if cols[7].text.strip() else 'N/A'
            minutes_played = unidecode(cols[8].text.strip()) if cols[8].text.strip() else 'N/A'
            assists = unidecode(cols[9].text.strip()) if cols[9].text.strip() else 'N/A'

            # Clean up market values
            if new_market_value.startswith('€'):
                new_market_value = new_market_value.replace('€', '').replace('m', ' Million').replace('k', ' Thousand')

            # Append data for the player
            all_players_data.append({
                'Name': name,
                'Position': position,
                'Club': Club,
                'Market Value (During Transfer)': new_market_value,
                'Goals Scored': goals_scored,
                'Minutes Played': minutes_played,
                'Assists': assists
            })

        # Pause for 2 seconds to avoid overwhelming the server
        print(f"Finished processing {league_name}, page {page}. Sleeping for 2 seconds...")
        time.sleep(2)

# Convert all the player data to a DataFrame
df = pd.DataFrame(all_players_data)

# Save the combined data to a CSV file
df.to_csv('new_arrival_performance.csv', index=False, encoding='utf-8')
print("Data collection completed and saved to 'new_arrival_performance.csv'")
