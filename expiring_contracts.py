import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from unidecode import unidecode

# URLs for five different leagues
leagues = {
    "La Liga": "https://www.transfermarkt.us/laliga/endendevertraege/wettbewerb/ES1/jahr/2025/land_id/0/ausrichtung/alle/spielerposition_id/alle/altersklasse/alle/plus/1",
    "Premier League": "https://www.transfermarkt.us/premier-league/endendevertraege/wettbewerb/GB1/jahr/2025/land_id/0/ausrichtung/alle/spielerposition_id/alle/altersklasse/alle/plus/1",
    "Serie A": "https://www.transfermarkt.us/serie-a/endendevertraege/wettbewerb/IT1/jahr/2025/land_id/0/ausrichtung/alle/spielerposition_id/alle/altersklasse/alle/plus/1",
    "Bundesliga": "https://www.transfermarkt.us/bundesliga/endendevertraege/wettbewerb/L1/jahr/2025/land_id/0/ausrichtung/alle/spielerposition_id/alle/altersklasse/alle/plus/1",
    "Ligue 1": "https://www.transfermarkt.us/ligue-1/endendevertraege/wettbewerb/FR1/jahr/2025/land_id/0/ausrichtung/alle/spielerposition_id/alle/altersklasse/alle/plus/1"
}

headers = {'User-Agent': 'Mozilla/5.0'}

# Empty list to hold all the players' data
all_players_data = []

# Maximum number of pages to check for each league
max_pages = 5

# Loop through each league
for league_name, base_url in leagues.items():
    print(f"Processing data for {league_name}...")

    # Loop through the pages (up to max_pages)
    for page in range(1, max_pages + 1):
        # Construct the URL for the current page
        if page == 1:
            url = base_url  # For the first page, use the base URL
        else:
            url = f"{base_url}/{page}"

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
        rows = table.find_all('tr')[1:]

        # Extract data from each row
        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 6:
                continue

            # Extract Number, Team Name, League, Market Value, and % Change
            name_tag = cols[0].find('img')
            name = unidecode(name_tag['title'] if name_tag else 'N/A')
            position = unidecode(cols[3].text.strip()) if cols[3].text.strip() else 'N/A'
            club_tag = cols[6].find('img')
            Club = unidecode(club_tag['title'] if club_tag else 'N/A')
            contract_end_date = unidecode(cols[7].text.strip()) if cols[7].text.strip() else 'N/A'
            market_value = unidecode(cols[9].text.strip()) if cols[9].text.strip() else 'N/A'
            fee_paid = unidecode(cols[10].text.strip()) if cols[10].text.strip() else 'N/A'
            agent = unidecode(cols[11].text.strip()) if cols[11].text.strip() else 'N/A'


            # Clean up market values
            if market_value.startswith('€'):
                market_value = market_value.replace('€', '').replace('m', ' Million').replace('k', ' Thousand')
            if fee_paid.startswith('€'):
                fee_paid = fee_paid.replace('€', '').replace('m', ' Million').replace('k', ' Thousand')

            # Append data for the player
            all_players_data.append({
                'Name': name,
                'Position': position,
                'Club': Club,
                'Contract End Date': contract_end_date,
                'Market Value': market_value,
                'Fee Paid': fee_paid,
                'Agent': agent
            })

        # Pause for 2 seconds to avoid overwhelming the server
        print(f"Finished processing {league_name}, page {page}. Sleeping for 2 seconds...")
        time.sleep(2)

# Convert all the player data to a DataFrame
df = pd.DataFrame(all_players_data)

# Save the combined data to a CSV file
df.to_csv('expiring_contracts.csv', index=False, encoding='utf-8')
print("Data collection completed and saved to 'expiring_contracts.csv'")