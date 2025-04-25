# GHL-Script-


FastAPI Redirect Service – Comprehensive Documentation
(plain-text, ready to paste into MS Word or any editor)

1. Purpose
This micro-service accepts a U S. ZIP code, determines the visitor’s state, looks up partner “funnel” URLs stored in a Google Sheet, and returns one of those URLs using a round-robin load-balancing strategy. If the ZIP code or state cannot be resolved, or no active partner exists, the service falls back to a default landing page.

2. High-Level Architecture
bash
Copy
Edit
Browser / Client ──► /redirect/{zip_code} ─┬─► uszipcode lookup
                                            │
                                            ├─► Google Sheet (CSV export)
                                            │
                                            └─► Round-robin selector
                                                        │
                                              JSON { "redirect_url": ... }
3. Technology Stack

Layer / Concern	Library / Service	Notes
Web framework	FastAPI	Async, automatic OpenAPI docs
CORS handling	fastapi.middleware.cors	Allows requests from any origin
HTTP client	requests	Fetches CSV export of the Google Sheet
Data wrangling	pandas	Reads & cleans the CSV in-memory
ZIP → State lookup	uszipcode	Local offline search engine
State tracking	In-process dict	Round-robin counters per state
4. Source Walk-Through
4.1 CORS Setup
python
Copy
Edit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
Allows any front-end (SPA, landing page, etc.) to call the service without pre-flight errors.

4.2 Google Sheet Access
SHEET_CSV_URL is the CSV download link for the “By State” tab (each state appears as a column header).

fetch_google_sheet() pulls the sheet on every request to ensure real-time accuracy, then:

Reads the raw CSV into a DataFrame.

Replaces NaN, inf, and -inf with empty strings so boolean tests remain predictable.

4.3 ZIP → State Resolution
python
Copy
Edit
search = SearchEngine(simple_zipcode=True)
zipcode_data = search.by_zipcode(zip_code)
state = zipcode_data.state  # returns "CA", "TX", etc.
If the ZIP is unknown or the library returns None, the request is routed to the default URL.

4.4 State Abbreviation Map
A constant dict translates two-letter abbreviations to full names that exactly match the Google Sheet column headers. If a new state is added to the sheet, also add it here.

4.5 Filtering Valid Companies
python
Copy
Edit
valid_companies = df[(df[state_full] == True) & (df["On/Off"] == True)]
At least two sheet columns are mandatory:

One column per state – must contain boolean TRUE (uppercase, without quotes) for each active company.

On/Off – global kill-switch per company row.

If the filter returns zero rows the user again receives the default landing page.

4.6 Round-Robin Selection
round_robin_state_tracker is an in-memory dictionary:
{"California": 5, "Texas": 2, ...}

Per incoming request:

Initialize the counter for the state if it does not exist.

Pick the company index counter % len(company_list).

Increment the counter (mod length) for next time.

Note: In multi-process deployments the tracker lives only inside one worker. For gunicorn/Docker/Kubernetes you need a shared store (Redis, database) to keep round-robin global. See § 8 Scalability.

5. API Specification

Method	Path	Description	Parameter	Response (HTTP 200)
GET	/redirect/{zip_code}	Returns best funnel URL for ZIP	zip_code – US 5-digit string	{"redirect_url": "https://..."}
All failure modes (unknown ZIP, unknown state, no partners) still return HTTP 200 with the default URL.

Example
bash
Copy
Edit
curl https://your-domain.com/redirect/94105
{"redirect_url":"https://partner-site.com/ca-offer"}
6. Environment & Installation
bash
Copy
Edit
# 1. Create environment
python -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install fastapi uvicorn pandas requests uszipcode python-multipart

# 3. Download uszipcode DB (first run triggers it automatically)
python -c "from uszipcode import SearchEngine; SearchEngine().update()"
Tip: Pin exact versions in requirements.txt for deterministic builds.

7. Running Locally
bash
Copy
Edit
uvicorn app:app --reload  # auto-reload for development
Open your browser at http://127.0.0.1:8000/redirect/10001.
Interactive docs live at http://127.0.0.1:8000/docs.

