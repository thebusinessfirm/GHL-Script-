# 🎯 FastAPI Redirect Service

> Resolve a U S. ZIP code, map it to the visitor’s state, look up active partner
> “funnel” links in a Google Sheet, and return one of those links using
> **round-robin** load balancing.  
> If no partner is available, users are redirected to a default fallback page.

---

## Table of Contents

1. [Features](#features)  
2. [Quick Start](#quick-start)  
3. [Project Structure](#project-structure)  
4. [Configuration](#configuration)  
5. [API Reference](#api-reference)  
6. [Deployment Guides](#deployment-guides)  
7. [Scaling Notes](#scaling-notes)  
8. [Troubleshooting](#troubleshooting)  
9. [Roadmap](#roadmap)  
10. [License](#license)

---

## Features

|                           | Description                                   |
|---------------------------|-----------------------------------------------|
| **FastAPI** backend       | Automatic OpenAPI docs & async-ready          |
| Google Sheet integration  | Reads live data from the “By State” tab       |
| ZIP → State resolution    | Offline lookup via `uszipcode`                |
| Round-robin load balance  | Even traffic distribution per state           |
| CORS enabled              | Can be called directly from any landing page  |
| Drop-in default fallback  | Always serves a valid URL, even on failure    |

---

## Quick Start

```bash
# 1 · Clone & enter
git clone https://github.com/your-org/redirect-service.git
cd redirect-service

# 2 · Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3 · Install dependencies
pip install -r requirements.txt

# 4 · Run database download for uszipcode (first run only)
python -c "from uszipcode import SearchEngine; SearchEngine().update()"

# 5 · Launch development server
uvicorn app:app --reload
```

Visit **`http://127.0.0.1:8000/docs`** for interactive Swagger UI.

---

## Project Structure

```
.
├── app.py              # FastAPI application
├── requirements.txt    # Locked dependencies
└── README.md
```

---

## Configuration

| Variable                  | Default value | Purpose                                                |
|---------------------------|---------------|--------------------------------------------------------|
| `SHEET_CSV_URL`           | Hard-coded    | CSV export link of the Google Sheet (“By State” tab)   |
| `DEFAULT_REDIRECT_URL`    | `https://retirementroadmaphub.com/one-page-5441` | Fallback URL |

> To change any of these, simply edit the top of **`app.py`** or move them to
> environment variables/config files as needed.

---

## API Reference

### `GET /redirect/{zip_code}`

| Parameter | Type   | Example | Description                          |
|-----------|--------|---------|--------------------------------------|
| `zip_code`| string | `90210` | U S. 5-digit ZIP (path parameter)    |

#### Successful Response `200 OK`

```json
{
  "redirect_url": "https://partner-site.com/ca-offer"
}
```

*All error conditions (unknown ZIP, unknown state, no active partner) still
return `200` with the **default** URL, ensuring your front-end always receives
a usable link.*

--



