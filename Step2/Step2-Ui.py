from flask import Flask, render_template, jsonify
import os
from datetime import datetime, timezone

app = Flask(__name__)

# Define the folder where your match text files are stored
matches_folder = 'matches/football'

# Function to read and parse the match data from the text files
def read_matches():
    matches = []
    current_time = datetime.now(timezone.utc)  # Get the current UTC time (timezone-aware)

    # Iterate over each file in the matches folder
    for filename in os.listdir(matches_folder):
        if filename.endswith('.txt'):
            match_data = {}
            # Read the match file
            with open(os.path.join(matches_folder, filename), 'r') as file:
                lines = file.readlines()
                for line in lines:
                    # Parse the relevant data from the file
                    if line.startswith('Match:'):
                        match_data['home_team'], match_data['away_team'] = line.split(': ')[1].strip().split(' vs ')
                    elif line.startswith('Start Date:'):
                        match_data['start_date'] = line.split(': ')[1].strip()
                        # Correctly pass the start_date string to datetime.fromisoformat
                        date_object = datetime.fromisoformat(match_data['start_date'])
                        formatted_date = date_object.strftime("%d/%m/%Y - %H:%M - %Z")
                        match_data['formatted_date'] = formatted_date

                        # Only add the match if it hasn't started yet
                        if date_object > current_time:  # Match has not started yet
                            matches.append(match_data)

                    elif line.startswith('Sport:'):
                        match_data['sport'] = line.split(': ')[1].strip()
                    elif line.startswith('Home Odds:'):
                        match_data['home_odds'] = float(line.split(': ')[1].strip())
                    elif line.startswith('Draw Odds:'):
                        match_data['draw_odds'] = float(line.split(': ')[1].strip())
                    elif line.startswith('Away Odds:'):
                        match_data['away_odds'] = float(line.split(': ')[1].strip())

    return matches

@app.route('/')
def index():
    # Render the main page (index.html) where the matches will be displayed
    return render_template('index.html')

@app.route('/matches')
def get_matches():
    # Get the match data and return it as JSON
    matches = read_matches()
    return jsonify(matches)

# Ensure the app runs properly in Vercel's serverless environment
if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True)
