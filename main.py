from fastapi import FastAPI
import pandas as pd
import requests
import io
from uszipcode import SearchEngine
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

# Add CORS middleware to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # This allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # This allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # This allows all headers
)

# Google Sheet CSV Link (Fetching "By State" Tab)
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1dtu2pC0u261I_PQchcAHmIH3Fvq9qvoIl-GAQHRgOBc/gviz/tq?tqx=out:csv&gid=2018349964"


# Round Robin State-wise Tracker
round_robin_state_tracker = {}

def fetch_google_sheet():
    """Fetch Google Sheet data dynamically from 'By State' tab"""
    response = requests.get(SHEET_CSV_URL)
    response.raise_for_status()  # Ensure successful request
    df = pd.read_csv(io.StringIO(response.text))  # Read CSV data
    df = df.fillna("").replace([float("inf"), float("-inf")], "")
    return df


# Initialize ZIP code search engine
search = SearchEngine(simple_zipcode=True)

@app.get("/redirect/{zip_code}")
def redirect_user(zip_code: str):
    """Handle user ZIP code as a path parameter and return the correct funnel link"""

    # Get State from ZIP code using uszipcode
    zipcode_data = search.by_zipcode(zip_code)
    if not zipcode_data or not zipcode_data.state:
        return {"redirect_url": "https://retirementroadmaphub.com/one-page-5441"}

    state = zipcode_data.state  # Get the state abbreviation (e.g., "NY" for New York)

    # Fetch latest data from Google Sheets
    df = fetch_google_sheet()

    # Convert state abbreviation to full state name
    state_full_name = {
        "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California",
        "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "FL": "Florida", "GA": "Georgia",
        "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa",
        "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
        "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri",
        "MT": "Montana", "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey",
        "NM": "New Mexico", "NY": "New York", "NC": "North Carolina", "ND": "North Dakota",
        "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island",
        "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
        "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin",
        "WY": "Wyoming"
    }

    state_full = state_full_name.get(state)
    if not state_full:
        return {"redirect_url": "https://retirementroadmaphub.com/one-page-5441"}

    # Ensure state column exists in the Google Sheet
    if state_full not in df.columns:
        return {"redirect_url": "https://retirementroadmaphub.com/one-page-5441"}

    # Filter companies that are ON and have `TRUE` in the selected state
    valid_companies = df[(df[state_full] == True) & (df["On/Off"] == True)]

    if valid_companies.empty:
        return {"redirect_url": "https://retirementroadmaphub.com/one-page-5441"}

    # Implement Round Robin Selection
    company_list = valid_companies["Funnel Link"].tolist()

    # Ensure Round Robin tracking works even when companies change
    if state_full not in round_robin_state_tracker:
        round_robin_state_tracker[state_full] = 0

    index = round_robin_state_tracker[state_full] % len(company_list)
    selected_link = company_list[index]

    # Move index forward for next request
    round_robin_state_tracker[state_full] = (index + 1) % len(company_list)

    return {"redirect_url": selected_link}
