# Whale Migration API

Local read-only FastAPI service for curated ocean and whale-related datasets.
It is designed for a university prototype where the API and frontend run on the same kiosk device using different local ports.

The API serves generated JSON files from source CSV datasets. It does not require a database, cloud deployment, authentication, or write operations.

## Quick Start

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the API:

```bash
python -m uvicorn app.main:app --reload
```

By default, the API runs at:

```text
http://127.0.0.1:8000
```

Useful local URLs:

```text
Root:   http://127.0.0.1:8000/
Health: http://127.0.0.1:8000/health
Docs:   http://127.0.0.1:8000/docs
```

To use another API port:

```bash
python -m uvicorn app.main:app --reload --port 9000
```

## Frontend Integration

Expected local setup:

```text
API:      http://127.0.0.1:8000
Frontend: http://localhost:3000
```

The frontend should call the API with an absolute URL:

```js
fetch("http://127.0.0.1:8000/ocean-warming/2020")
  .then((response) => response.json())
  .then((data) => console.log(data))
  .catch((error) => console.error(error));
```

The API is configured for local browser CORS. It accepts frontend requests from local origins on any port:

```text
http://localhost:any-port
http://127.0.0.1:any-port
http://[::1]:any-port
```

This supports common frontend ports such as `3000`, `5173`, and `5500` without allowing arbitrary external websites.

Avoid opening the frontend directly with `file://`. Use a local frontend server instead.

## Project Structure

```text
whale_api/
├── app/
│   ├── data/
│   │   ├── commercial_whaling.json
│   │   ├── marine_microplastics.json
│   │   ├── ocean_acidification.json
│   │   └── ocean_warming.json
│   └── main.py
├── datasets/
│   ├── marine_microplastics.csv
│   ├── ocean_acidification.csv
│   ├── ocean_warming.csv
│   └── whale_catch.csv
├── scripts/
│   └── build_datasets.py
├── README.md
├── requirements.txt
└── .gitignore
```

## Dataset Pipeline

The CSV files in `datasets/` are the source of truth.

Pipeline:

```text
datasets/*.csv -> scripts/build_datasets.py -> app/data/*.json -> FastAPI endpoints
```

Regenerate API JSON files after changing any source CSV:

```bash
python3 scripts/build_datasets.py
```

Current generated outputs:

```text
ocean_warming.json:          65 records
ocean_acidification.json:   500 records
commercial_whaling.json:    100 records
marine_microplastics.json:  648 records
```

Do not edit `app/data/*.json` by hand unless you intentionally want to bypass the CSV build pipeline.

## Active Datasets

| Dataset | Source CSV | API JSON | Scope |
| --- | --- | --- | --- |
| `ocean_warming` | `datasets/ocean_warming.csv` | `app/data/ocean_warming.json` | Annual ocean heat content values, 1957-2021 |
| `ocean_acidification` | `datasets/ocean_acidification.csv` | `app/data/ocean_acidification.json` | Environmental observations, 2015-2023 |
| `commercial_whaling` | `datasets/whale_catch.csv` | `app/data/commercial_whaling.json` | Southern Hemisphere whale catch records, 1900-1999 |
| `marine_microplastics` | `datasets/marine_microplastics.csv` | `app/data/marine_microplastics.json` | Southern Hemisphere measurements using `pieces/m3`, 2001-2020 |

Notes:

- `commercial_whaling` keeps only `Southern Hemisphere` rows from the source CSV.
- `marine_microplastics` keeps only Southern Hemisphere rows with unit `pieces/m3`.
- `ocean_acidification` currently includes environmental observations from both hemispheres.
- `ocean_warming` exposes integer years while preserving the source midpoint field as `source_year_midpoint`.

## API Endpoints

Base routes:

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/` | API landing response |
| `GET` | `/health` | Health check |
| `GET` | `/datasets` | Available dataset endpoint names |

Ocean warming:

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/ocean-warming` | Full annual series |
| `GET` | `/ocean-warming/{year}` | Single year |
| `GET` | `/ocean-warming/range?start_year=2018&end_year=2020` | Year range |

Ocean acidification:

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/ocean-acidification?limit=10` | Records, optionally limited |
| `GET` | `/ocean-acidification/date/{date}` | Records for one `YYYY-MM-DD` date |
| `GET` | `/ocean-acidification/range?start_date=2015-01-01&end_date=2015-01-20&limit=10` | Date range, optionally limited |
| `GET` | `/ocean-acidification/location/{location}?limit=10` | Records for one location |
| `GET` | `/ocean-acidification/locations` | Available locations |

Commercial whaling:

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/commercial-whaling` | Full Southern Hemisphere series |
| `GET` | `/commercial-whaling/{year}` | Single year |
| `GET` | `/commercial-whaling/range?start_year=1900&end_year=1904` | Year range |
| `GET` | `/commercial-whaling/species/{species}` | Full series for one species field |
| `GET` | `/commercial-whaling/species/{species}/range?start_year=1900&end_year=1904` | Species series by year range |

Marine microplastics:

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/marine-microplastics?limit=10` | Records, optionally limited |
| `GET` | `/marine-microplastics/date/{date}` | Records for one `YYYY-MM-DD` date |
| `GET` | `/marine-microplastics/range?start_date=2015-08-11&end_date=2017-01-21&limit=10` | Date range, optionally limited |
| `GET` | `/marine-microplastics/ocean/{ocean}?limit=10` | Records for one ocean |
| `GET` | `/marine-microplastics/oceans` | Available oceans |

## Common Request Examples

Get one ocean warming record:

```bash
curl http://127.0.0.1:8000/ocean-warming/2020
```

Response shape:

```json
{
  "year": 2020,
  "source_year_midpoint": 2020.5,
  "world_ohc_zj": 25.186,
  "world_ohc_se_zj": 0.183,
  "northern_hemisphere_ohc_zj": 11.596,
  "northern_hemisphere_ohc_se_zj": 0.087,
  "southern_hemisphere_ohc_zj": 13.591,
  "southern_hemisphere_ohc_se_zj": 0.095
}
```

Get a limited microplastics response:

```bash
curl "http://127.0.0.1:8000/marine-microplastics?limit=2"
```

Get available commercial whaling species fields:

```text
all_whale_species
blue_whale
brydes_whale
fin_whale
gray_whale
humpback_whale
minke_whale
right_whale
sei_whale
sperm_whale
unspecified_other_species
```

Example species request:

```bash
curl "http://127.0.0.1:8000/commercial-whaling/species/humpback_whale/range?start_year=1900&end_year=1904"
```

## Error Behavior

The API uses standard HTTP responses:

| Status | When it happens |
| --- | --- |
| `200` | Request succeeded |
| `400` | Invalid input, such as a reversed date or year range |
| `404` | No matching record or unsupported path value |
| `422` | FastAPI validation error, such as a missing required query parameter |
| `500` | Generated JSON file is missing valid structure |

Example:

```bash
curl http://127.0.0.1:8000/ocean-warming/1900
```

```json
{
  "detail": "No ocean warming record found for year 1900."
}
```

## Verification

Basic local checks:

```bash
python -m compileall app scripts
python3 scripts/build_datasets.py
```

With the server running:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/datasets
```

Expected health response:

```json
{
  "status": "ok"
}
```

## Current Scope

- The API is read-only.
- The intended deployment is local kiosk usage, not cloud hosting.
- The frontend and backend are expected to run on the same device.
- FastAPI interactive docs are available at `/docs`.
- Source CSV files remain unchanged by the API at runtime.
