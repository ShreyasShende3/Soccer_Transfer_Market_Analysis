import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from unidecode import unidecode


base_url = 'https://www.transfermarkt.us/statistik/saisontransfers?ajax=yw0&page={}&sort=marktwert_zeitpunkt.desc'


headers = {'User-Agent': 'Mozilla/5.0'}


players_data = []


for page in range(1, 81):
    print(f"Processing page {page}...")

    url = base_url.format(page)

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        response.encoding = 'utf-8'
    except requests.RequestException as e:
        print(f"Error fetching page {page}: {e}")
        continue

    soup = BeautifulSoup(response.content.decode('utf-8', 'ignore'), 'html.parser')

    table = soup.find('table', {'class': 'items'})
    if not table:
        print(f"Error: Table not found on page {page}")
        continue

    rows = table.find_all('tr')[1:]

    # Extract data row by row
    for idx, row in enumerate(rows):
        cols = row.find_all('td')

        if len(cols) < 6:
            continue

        # Extract player name and position
        player_name = unidecode(cols[3].find('a').text.strip()) if cols[1].find('a') else 'N/A'
        position = unidecode(cols[4].text.strip()) if cols[4].text.strip() else 'N/A'

        # Age
        age = unidecode(cols[5].text.strip()) if cols[5].text.strip() else 'N/A'

        # Market Value (clean up the format)
        market_value = unidecode(cols[6].text.strip()) if cols[6].text.strip() else 'N/A'
        if market_value.startswith('€'):
            market_value = market_value.replace('€', '').replace('m', ' Million').replace('k', ' Thousand')

        # Nationality
        nationality_tag = cols[7].find('img')
        nationality = nationality_tag['title'] if nationality_tag else 'N/A'

        # Joined club and league (apply unidecode here as well)
        joined_club_tag = cols[10].find('a')
        joined_club = unidecode(joined_club_tag.text.strip()) if joined_club_tag else 'N/A'
        joined_league_tag = cols[11].find('a')
        joined_league = unidecode(joined_league_tag.text.strip()) if joined_league_tag else 'N/A'

        # Transfer Fee (clean up the format)
        fee = unidecode(cols[12].text.strip()) if cols[12].text.strip() else 'N/A'
        if fee.startswith('€'):
            fee = fee.replace('€', '').replace('m', ' Million').replace('k', ' Thousand')

        # Append to the list
        players_data.append({
            'Player': player_name,
            'Position': position,
            'Age': age,
            'Market Value': market_value,
            'Nationality': nationality,
            'Joined Club': joined_club,
            'Joined League': joined_league,
            'Transfer Fee': fee
        })

    # Sleep for 2 seconds after processing each page
    print(f"Finished page {page}. Sleeping for 2 seconds...")
    time.sleep(2)

# Convert the data into a DataFrame
df = pd.DataFrame(players_data)

# Save to CSV
df.to_csv('transfers.csv', index=False)
print("Data saved to transfers.csv")
