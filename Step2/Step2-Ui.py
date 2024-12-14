from flask import Flask, render_template, jsonify, request
import os
import pandas as pd
from datetime import datetime, timezone

app = Flask(__name__)

# Path to the new MatchManager.xlsx file
match_manager_file = 'matches/MatchManager.xlsx'


def read_matches(sport=None, date=None):
    matches = []
    current_time = datetime.now(timezone.utc)

    if not os.path.exists(match_manager_file):
        print(f"Error: '{match_manager_file}' does not exist.")
        return matches

    # Read the Excel file into a pandas DataFrame
    df = pd.read_excel(match_manager_file)

    # Filter out rows that contain random data (like 'Payload')
    df = df[~df['Identifier'].str.contains('Payload', na=False)]

    # Filter out rows with missing required values (Date, Time, Team 1, Team 2)
    df = df.dropna(subset=['Date', 'Time', 'Team 1', 'Team 2'])

    for index, row in df.iterrows():
        match_data = {}

        # Extract match details
        match_data['home_team'] = row['Team 1']
        match_data['away_team'] = row['Team 2']

        # Handle the Date and Time fields properly
        date_value = row['Date']
        time_value = row['Time']

        if isinstance(date_value, (datetime, str)) and isinstance(time_value, str):
            if isinstance(date_value, datetime):
                match_data['start_date'] = date_value.strftime('%Y-%m-%d %H:%M:%S')
            else:
                match_data['start_date'] = date_value.strip() + ' ' + time_value.strip()

        else:
            print(
                f"Skipping invalid date or time: {date_value} {time_value} (Match: {row['Team 1']} vs {row['Team 2']})")
            continue

        match_data['sport'] = row['Sport']

        # Map the odds to more intuitive names
        match_data['odds'] = {
            'home_odds': row['1X2 1'],  # Home team win odds
            'draw_odds': row['1X2 X'],  # Draw odds
            'away_odds': row['1X2 2'],  # Away team win odds
            'bts_yes': row['BTS Yes'],  # BTS Yes odds
            'bts_no': row['BTS No'],  # BTS No odds
            'dc_1x': row['DC 1X'],  # Double Chance Home/Draw
            'dc_12': row['DC 12'],  # Double Chance Home/Away
            'dc_x2': row['DC X2'],  # Double Chance Draw/Away
            'dnb_1': row['DNB 1'],  # Draw No Bet Home
            'dnb_2': row['DNB 2'],  # Draw No Bet Away
        }

        # Convert 'start_date' to datetime and make it timezone-aware
        try:
            date_object = datetime.strptime(match_data['start_date'], '%Y-%m-%d %H:%M:%S')
            date_object = date_object.replace(tzinfo=timezone.utc)

            match_data['formatted_date'] = date_object.strftime("%d/%m/%Y - %H:%M - %Z")
            if date_object > current_time:
                matches.append(match_data)
        except ValueError:
            print(
                f"Skipping invalid date: {match_data['start_date']} (Match: {match_data['home_team']} vs {match_data['away_team']})")

    return matches



@app.route('/')
def index():
    # Render the main page where the matches will be displayed
    return render_template('index.html')


@app.route('/matches')
def get_matches():
    sport = request.args.get('sport')
    date = request.args.get('date')
    matches = read_matches(sport, date)
    return jsonify(matches)


@app.route('/sports')
def get_sports():
    sports = set()
    if not os.path.exists(match_manager_file):
        return jsonify([])

    # Read the Excel file into a pandas DataFrame
    df = pd.read_excel(match_manager_file)

    # Filter out rows that contain random data (like 'Payload')
    df = df[~df['Identifier'].str.contains('Payload', na=False)]

    # Extract the sports
    sports = set(df['Sport'].dropna())

    return jsonify(list(sports))


@app.route('/dates')
def get_dates():
    sport = request.args.get('sport')
    dates = set()
    if not os.path.exists(match_manager_file):
        return jsonify([])

    # Read the Excel file into a pandas DataFrame
    df = pd.read_excel(match_manager_file)

    # Filter out rows that contain random data (like 'Payload')
    df = df[~df['Identifier'].str.contains('Payload', na=False)]

    # Extract the dates
    if sport:
        df = df[df['Sport'].str.lower() == sport.lower()]

    # Add dates (we assume 'Date' is in 'YYYY-MM-DD' format)
    dates = set(df['Date'].dropna())

    return jsonify(sorted(dates))


if __name__ == '__main__':
    app.run(debug=False)



 # # # NEW MODIFYY!!!! !!!
