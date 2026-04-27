# Whale Migration API

Local FastAPI project for serving curated ocean and whale-related datasets for a prototype focused on whale migration, ocean conditions, and human pressures in the Southern Hemisphere.

## Overview

This repository turns source CSV files into clean JSON payloads and exposes them through a read-only API.

The current API focuses on four datasets:

- `ocean_warming`: annual ocean heat content series with global and hemispheric values
- `ocean_acidification`: environmental observations such as pH, SST, bleaching severity, and marine heatwaves
- `commercial_whaling`: Southern Hemisphere subset of historical whale catch records
- `marine_microplastics`: Southern Hemisphere subset of geolocated microplastic measurements

The API is intentionally read-only. All public routes are `GET` endpoints designed for data display, prototyping, and visualization.

## Features

- FastAPI-based local API
- CSV to JSON build pipeline
- Ocean warming routes by full series, by year, and by year range
- Read-only dataset responses ready for frontend consumption

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

The project keeps source files and API-ready files separate.

1. Source CSV files live in `datasets/`
2. `scripts/build_datasets.py` cleans and transforms those files
3. Final JSON payloads are written to `app/data/`
4. FastAPI serves the JSON through `GET` endpoints

This keeps the original files untouched while giving the API a fast and simple JSON layer.

## Active Datasets

### Ocean Warming

Source file:
- `datasets/ocean_warming.csv`

API file:
- `app/data/ocean_warming.json`

Useful fields:
- `year`
- `source_year_midpoint`
- `world_ohc_zj`
- `world_ohc_se_zj`
- `northern_hemisphere_ohc_zj`
- `northern_hemisphere_ohc_se_zj`
- `southern_hemisphere_ohc_zj`
- `southern_hemisphere_ohc_se_zj`

Note:
- The source stores annual values as midpoints like `1957.5`
- The API exposes a cleaner integer `year` for lookups such as `/ocean-warming/1957`

### Ocean Acidification

Source file:
- `datasets/ocean_acidification.csv`

API file:
- `app/data/ocean_acidification.json`

Useful fields:
- `date`
- `location`
- `latitude`
- `longitude`
- `sst_c`
- `ph_level`
- `bleaching_severity`
- `species_observed`
- `marine_heatwave`

### Commercial Whaling

Source file:
- `datasets/whale_catch.csv`

API file:
- `app/data/commercial_whaling.json`

Cleaning rule:
- only `Southern Hemisphere` rows are kept

Useful fields:
- `year`
- `all_whale_species`
- `humpback_whale`
- `minke_whale`
- `blue_whale`
- `fin_whale`
- other species-specific columns

### Marine Microplastics

Source file:
- `datasets/marine_microplastics.csv`

API file:
- `app/data/marine_microplastics.json`

Cleaning rules:
- only Southern Hemisphere rows are kept
- only records with unit `pieces/m3` are kept

Useful fields:
- `ocean`
- `region`
- `subregion`
- `sampling_method`
- `measurement_pieces_m3`
- `density_class`
- `latitude`
- `longitude`
- `date`

## API Endpoints

### Base Routes

- `GET /`
- `GET /health`
- `GET /datasets`

### Dataset Routes

- `GET /ocean-warming`
- `GET /ocean-warming/{year}`
- `GET /ocean-warming/range?start_year=1957&end_year=1965`
- `GET /ocean-acidification`
- `GET /ocean-acidification/date/{date}`
- `GET /ocean-acidification/range?start_date=2015-01-01&end_date=2015-01-20`
- `GET /ocean-acidification/location/{location}`
- `GET /ocean-acidification/locations`
- `GET /commercial-whaling`
- `GET /commercial-whaling/{year}`
- `GET /commercial-whaling/range?start_year=1900&end_year=1902`
- `GET /commercial-whaling/species/{species}`
- `GET /commercial-whaling/species/{species}/range?start_year=1900&end_year=1904`
- `GET /marine-microplastics`
- `GET /marine-microplastics/date/{date}`
- `GET /marine-microplastics/range?start_date=2015-08-11&end_date=2017-01-21`
- `GET /marine-microplastics/ocean/{ocean}`
- `GET /marine-microplastics/oceans`

## Example Responses

### `GET /ocean-warming/2020`

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

### `GET /ocean-warming/range?start_year=2018&end_year=2020`

```json
[
  {
    "year": 2018,
    "source_year_midpoint": 2018.5,
    "world_ohc_zj": 23.294,
    "southern_hemisphere_ohc_zj": 12.411
  },
  {
    "year": 2019,
    "source_year_midpoint": 2019.5,
    "world_ohc_zj": 24.442,
    "southern_hemisphere_ohc_zj": 12.999
  },
  {
    "year": 2020,
    "source_year_midpoint": 2020.5,
    "world_ohc_zj": 25.186,
    "southern_hemisphere_ohc_zj": 13.591
  }
]
```

### `GET /ocean-acidification?limit=2`

```json
[
  {
    "date": "2015-01-01",
    "location": "Red Sea",
    "latitude": 20.0248,
    "longitude": 38.4931,
    "sst_c": 29.47,
    "ph_level": 8.107,
    "bleaching_severity": "None",
    "species_observed": 106,
    "marine_heatwave": false
  },
  {
    "date": "2015-01-07",
    "location": "Great Barrier Reef",
    "latitude": -18.2988,
    "longitude": 147.7782,
    "sst_c": 29.65,
    "ph_level": 8.004,
    "bleaching_severity": "High",
    "species_observed": 116,
    "marine_heatwave": false
  }
]
```

### `GET /ocean-acidification/date/2015-01-07`

```json
[
  {
    "date": "2015-01-07",
    "location": "Great Barrier Reef",
    "latitude": -18.2988,
    "longitude": 147.7782,
    "sst_c": 29.65,
    "ph_level": 8.004,
    "bleaching_severity": "High",
    "species_observed": 116,
    "marine_heatwave": false
  }
]
```

### `GET /ocean-acidification/range?start_date=2015-01-01&end_date=2015-01-20`

```json
[
  {
    "date": "2015-01-01",
    "location": "Red Sea",
    "latitude": 20.0248,
    "longitude": 38.4931,
    "sst_c": 29.47,
    "ph_level": 8.107,
    "bleaching_severity": "None",
    "species_observed": 106,
    "marine_heatwave": false
  },
  {
    "date": "2015-01-07",
    "location": "Great Barrier Reef",
    "latitude": -18.2988,
    "longitude": 147.7782,
    "sst_c": 29.65,
    "ph_level": 8.004,
    "bleaching_severity": "High",
    "species_observed": 116,
    "marine_heatwave": false
  },
  {
    "date": "2015-01-14",
    "location": "Caribbean Sea",
    "latitude": 14.9768,
    "longitude": -75.0233,
    "sst_c": 28.86,
    "ph_level": 7.947,
    "bleaching_severity": "High",
    "species_observed": 90,
    "marine_heatwave": false
  },
  {
    "date": "2015-01-20",
    "location": "Great Barrier Reef",
    "latitude": -18.3152,
    "longitude": 147.6486,
    "sst_c": 28.97,
    "ph_level": 7.995,
    "bleaching_severity": "Medium",
    "species_observed": 94,
    "marine_heatwave": false
  }
]
```

### `GET /ocean-acidification/location/Great%20Barrier%20Reef?limit=3`

```json
[
  {
    "date": "2015-01-07",
    "location": "Great Barrier Reef",
    "latitude": -18.2988,
    "longitude": 147.7782,
    "sst_c": 29.65,
    "ph_level": 8.004,
    "bleaching_severity": "High",
    "species_observed": 116,
    "marine_heatwave": false
  },
  {
    "date": "2015-01-20",
    "location": "Great Barrier Reef",
    "latitude": -18.3152,
    "longitude": 147.6486,
    "sst_c": 28.97,
    "ph_level": 7.995,
    "bleaching_severity": "Medium",
    "species_observed": 94,
    "marine_heatwave": false
  },
  {
    "date": "2015-05-12",
    "location": "Great Barrier Reef",
    "latitude": -18.3579,
    "longitude": 147.6782,
    "sst_c": 27.99,
    "ph_level": 8.02,
    "bleaching_severity": "None",
    "species_observed": 122,
    "marine_heatwave": false
  }
]
```

### `GET /ocean-acidification/locations`

```json
[
  "Caribbean Sea",
  "Galápagos",
  "Great Barrier Reef",
  "Hawaiian Islands",
  "Maldives",
  "Red Sea",
  "South China Sea"
]
```

### `GET /commercial-whaling/1904`

```json
{
  "hemisphere": "Southern Hemisphere",
  "code": "OWID_SH",
  "year": 1904,
  "all_whale_species": 203,
  "brydes_whale": 0,
  "gray_whale": null,
  "minke_whale": 0,
  "sei_whale": 0,
  "unspecified_other_species": 0,
  "blue_whale": 11,
  "fin_whale": 4,
  "humpback_whale": 188,
  "right_whale": 0,
  "sperm_whale": 0
}
```

### `GET /commercial-whaling/range?start_year=1900&end_year=1902`

```json
[
  {
    "hemisphere": "Southern Hemisphere",
    "code": "OWID_SH",
    "year": 1900,
    "all_whale_species": 8,
    "brydes_whale": 0,
    "gray_whale": null,
    "minke_whale": 0,
    "sei_whale": 0,
    "unspecified_other_species": 0,
    "blue_whale": 0,
    "fin_whale": 0,
    "humpback_whale": 8,
    "right_whale": 0,
    "sperm_whale": 0
  },
  {
    "hemisphere": "Southern Hemisphere",
    "code": "OWID_SH",
    "year": 1901,
    "all_whale_species": 8,
    "brydes_whale": 0,
    "gray_whale": null,
    "minke_whale": 0,
    "sei_whale": 0,
    "unspecified_other_species": 0,
    "blue_whale": 0,
    "fin_whale": 0,
    "humpback_whale": 8,
    "right_whale": 0,
    "sperm_whale": 0
  },
  {
    "hemisphere": "Southern Hemisphere",
    "code": "OWID_SH",
    "year": 1902,
    "all_whale_species": 8,
    "brydes_whale": 0,
    "gray_whale": null,
    "minke_whale": 0,
    "sei_whale": 0,
    "unspecified_other_species": 0,
    "blue_whale": 0,
    "fin_whale": 0,
    "humpback_whale": 8,
    "right_whale": 0,
    "sperm_whale": 0
  }
]
```

### `GET /commercial-whaling/species/humpback_whale`

This route returns the full Southern Hemisphere time series for `humpback_whale` from `1900` to `1999`.
Each record uses the shape below:

```json
{
  "year": 1900,
  "hemisphere": "Southern Hemisphere",
  "species": "humpback_whale",
  "catch_count": 8
}
```

### `GET /commercial-whaling/species/humpback_whale/range?start_year=1900&end_year=1904`

```json
[
  {
    "year": 1900,
    "hemisphere": "Southern Hemisphere",
    "species": "humpback_whale",
    "catch_count": 8
  },
  {
    "year": 1901,
    "hemisphere": "Southern Hemisphere",
    "species": "humpback_whale",
    "catch_count": 8
  },
  {
    "year": 1902,
    "hemisphere": "Southern Hemisphere",
    "species": "humpback_whale",
    "catch_count": 8
  },
  {
    "year": 1903,
    "hemisphere": "Southern Hemisphere",
    "species": "humpback_whale",
    "catch_count": 9
  },
  {
    "year": 1904,
    "hemisphere": "Southern Hemisphere",
    "species": "humpback_whale",
    "catch_count": 188
  }
]
```

### `GET /marine-microplastics?limit=2`

```json
[
  {
    "ocean": "Atlantic Ocean",
    "region": null,
    "subregion": null,
    "sampling_method": "Grab sample",
    "measurement_pieces_m3": 0.018,
    "unit": "pieces/m3",
    "density_range": "0.005-1",
    "density_class": "Medium",
    "short_reference": "Barrows et al.2018",
    "doi": "https://doi.org/10.1016/j.envpol.2018.02.062",
    "organization": "Adventure Scientist",
    "keywords": "Adventure Scientist/Citizen Science",
    "accession_number": "211009",
    "accession_link": "https://www.ncei.noaa.gov/access/metadata/landing-page/bin/iso?id=gov.noaa.nodc:211009",
    "latitude": -31.696,
    "longitude": -48.56,
    "date": "2015-08-11"
  },
  {
    "ocean": "Atlantic Ocean",
    "region": null,
    "subregion": null,
    "sampling_method": "Grab sample",
    "measurement_pieces_m3": 0.001,
    "unit": "pieces/m3",
    "density_range": "0.0005-0.005",
    "density_class": "Low",
    "short_reference": "Barrows et al.2018",
    "doi": "https://doi.org/10.1016/j.envpol.2018.02.062",
    "organization": "Adventure Scientist",
    "keywords": "Adventure Scientist/Citizen Science",
    "accession_number": "211009",
    "accession_link": "https://www.ncei.noaa.gov/access/metadata/landing-page/bin/iso?id=gov.noaa.nodc:211009",
    "latitude": -40.3233,
    "longitude": -9.8962,
    "date": "2017-01-21"
  }
]
```

### `GET /marine-microplastics/date/2015-08-11`

```json
[
  {
    "ocean": "Atlantic Ocean",
    "region": null,
    "subregion": null,
    "sampling_method": "Grab sample",
    "measurement_pieces_m3": 0.018,
    "unit": "pieces/m3",
    "density_range": "0.005-1",
    "density_class": "Medium",
    "short_reference": "Barrows et al.2018",
    "doi": "https://doi.org/10.1016/j.envpol.2018.02.062",
    "organization": "Adventure Scientist",
    "keywords": "Adventure Scientist/Citizen Science",
    "accession_number": "211009",
    "accession_link": "https://www.ncei.noaa.gov/access/metadata/landing-page/bin/iso?id=gov.noaa.nodc:211009",
    "latitude": -31.696,
    "longitude": -48.56,
    "date": "2015-08-11"
  }
]
```

### `GET /marine-microplastics/range?start_date=2015-08-11&end_date=2017-01-21&limit=5`

```json
[
  {
    "ocean": "Atlantic Ocean",
    "region": null,
    "subregion": null,
    "sampling_method": "Grab sample",
    "measurement_pieces_m3": 0.018,
    "unit": "pieces/m3",
    "density_range": "0.005-1",
    "density_class": "Medium",
    "short_reference": "Barrows et al.2018",
    "doi": "https://doi.org/10.1016/j.envpol.2018.02.062",
    "organization": "Adventure Scientist",
    "keywords": "Adventure Scientist/Citizen Science",
    "accession_number": "211009",
    "accession_link": "https://www.ncei.noaa.gov/access/metadata/landing-page/bin/iso?id=gov.noaa.nodc:211009",
    "latitude": -31.696,
    "longitude": -48.56,
    "date": "2015-08-11"
  },
  {
    "ocean": "Atlantic Ocean",
    "region": null,
    "subregion": null,
    "sampling_method": "Grab sample",
    "measurement_pieces_m3": 0.001,
    "unit": "pieces/m3",
    "density_range": "0.0005-0.005",
    "density_class": "Low",
    "short_reference": "Barrows et al.2018",
    "doi": "https://doi.org/10.1016/j.envpol.2018.02.062",
    "organization": "Adventure Scientist",
    "keywords": "Adventure Scientist/Citizen Science",
    "accession_number": "211009",
    "accession_link": "https://www.ncei.noaa.gov/access/metadata/landing-page/bin/iso?id=gov.noaa.nodc:211009",
    "latitude": -40.3233,
    "longitude": -9.8962,
    "date": "2017-01-21"
  },
  {
    "ocean": "Pacific Ocean",
    "region": null,
    "subregion": null,
    "sampling_method": "AVANI net",
    "measurement_pieces_m3": 0.085555,
    "unit": "pieces/m3",
    "density_range": "0.005-1",
    "density_class": "Medium",
    "short_reference": "Eriksen et al.2018",
    "doi": "https://doi.org/10.1016/j.envpol.2017.09.058",
    "organization": "5 Gyres Institute",
    "keywords": "AVANI Net; SV Mir; RV Cabo de Hornos",
    "accession_number": "275967",
    "accession_link": "https://www.ncei.noaa.gov/access/metadata/landing-page/bin/iso?id=gov.noaa.nodc:275967",
    "latitude": -27.013,
    "longitude": -107.57014,
    "date": "2015-10-27"
  },
  {
    "ocean": "Pacific Ocean",
    "region": null,
    "subregion": null,
    "sampling_method": "Neuston net",
    "measurement_pieces_m3": 0.056245,
    "unit": "pieces/m3",
    "density_range": "0.005-1",
    "density_class": "Medium",
    "short_reference": "Eriksen et al.2018",
    "doi": "https://doi.org/10.1016/j.envpol.2017.09.058",
    "organization": "5 Gyres Institute",
    "keywords": "AVANI Net; SV Mir; RV Cabo de Hornos",
    "accession_number": "275967",
    "accession_link": "https://www.ncei.noaa.gov/access/metadata/landing-page/bin/iso?id=gov.noaa.nodc:275967",
    "latitude": -26.46396,
    "longitude": -105.36589,
    "date": "2015-11-03"
  },
  {
    "ocean": "Pacific Ocean",
    "region": null,
    "subregion": null,
    "sampling_method": "Manta net",
    "measurement_pieces_m3": 0.004951,
    "unit": "pieces/m3",
    "density_range": "0.0005-0.005",
    "density_class": "Low",
    "short_reference": "Faure et al.2015",
    "doi": "https://doi.org/10.1007/s11356-015-4453-3",
    "organization": "Oceaneye Association,  Switzerland",
    "keywords": "Oceaneye Association; Citizen Science",
    "accession_number": "276422",
    "accession_link": "https://www.ncei.noaa.gov/access/metadata/landing-page/bin/iso?id=gov.noaa.nodc:276422",
    "latitude": -45.15,
    "longitude": -73.635,
    "date": "2016-01-21"
  }
]
```

### `GET /marine-microplastics/ocean/Atlantic%20Ocean?limit=3`

```json
[
  {
    "ocean": "Atlantic Ocean",
    "region": null,
    "subregion": null,
    "sampling_method": "Grab sample",
    "measurement_pieces_m3": 0.018,
    "unit": "pieces/m3",
    "density_range": "0.005-1",
    "density_class": "Medium",
    "short_reference": "Barrows et al.2018",
    "doi": "https://doi.org/10.1016/j.envpol.2018.02.062",
    "organization": "Adventure Scientist",
    "keywords": "Adventure Scientist/Citizen Science",
    "accession_number": "211009",
    "accession_link": "https://www.ncei.noaa.gov/access/metadata/landing-page/bin/iso?id=gov.noaa.nodc:211009",
    "latitude": -31.696,
    "longitude": -48.56,
    "date": "2015-08-11"
  },
  {
    "ocean": "Atlantic Ocean",
    "region": null,
    "subregion": null,
    "sampling_method": "Grab sample",
    "measurement_pieces_m3": 0.001,
    "unit": "pieces/m3",
    "density_range": "0.0005-0.005",
    "density_class": "Low",
    "short_reference": "Barrows et al.2018",
    "doi": "https://doi.org/10.1016/j.envpol.2018.02.062",
    "organization": "Adventure Scientist",
    "keywords": "Adventure Scientist/Citizen Science",
    "accession_number": "211009",
    "accession_link": "https://www.ncei.noaa.gov/access/metadata/landing-page/bin/iso?id=gov.noaa.nodc:211009",
    "latitude": -40.3233,
    "longitude": -9.8962,
    "date": "2017-01-21"
  },
  {
    "ocean": "Atlantic Ocean",
    "region": null,
    "subregion": null,
    "sampling_method": "Neuston net",
    "measurement_pieces_m3": 3.218619,
    "unit": "pieces/m3",
    "density_range": "1-10",
    "density_class": "High",
    "short_reference": "Eriksen et al.2014",
    "doi": "https://doi.org/10.1371/journal.pone.0111913",
    "organization": "5 Gyres Institute",
    "keywords": "SV Mir; ORV Alguita; SV Sea Dragon; RV Stad Amsterdam",
    "accession_number": "275968",
    "accession_link": "https://www.ncei.noaa.gov/access/metadata/landing-page/bin/iso?id=gov.noaa.nodc:275968",
    "latitude": -30.5678,
    "longitude": -22.9272,
    "date": "2011-01-23"
  }
]
```

### `GET /marine-microplastics/oceans`

```json
[
  "Atlantic Ocean",
  "Indian Ocean",
  "Pacific Ocean"
]
```

## Local Development

### 1. Clone the repository

```bash
git clone https://github.com/jorec806/whale_api.git
cd whale_api
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the API

Use the module form so the project always runs with the Python interpreter from the virtual environment.

```bash
python -m uvicorn app.main:app --reload
```

By default, Uvicorn serves the API on port `8000`.

If you need a different port, start the server with `--port`:

```bash
python -m uvicorn app.main:app --reload --port 9000
```

### 5. Open the API locally

- Root: `http://127.0.0.1:8000/`
- Docs: `http://127.0.0.1:8000/docs`

### Minimal JavaScript example

The simplest possible way to consume the API from frontend JavaScript is:

```js
fetch("http://127.0.0.1:8000/ocean-warming/2020")
  .then((response) => response.json())
  .then((data) => console.log(data))
  .catch((error) => console.error(error));
```

This example uses the default local Uvicorn port `8000`.
If you start the server on a different port, update the URL accordingly.

For pages served by the same FastAPI app, a relative request is more portable:

```js
fetch("/ocean-warming/2020")
  .then((response) => response.json())
  .then((data) => console.log(data))
  .catch((error) => console.error(error));
```

## Current Status

- The four main datasets are already cleaned into JSON
- `ocean-warming` now supports lookup by year and by range
- `ocean-acidification` now supports lookup by date, date range, location, and available locations
- `commercial-whaling` now supports lookup by year, by range, and by species
- `marine-microplastics` now supports lookup by date, date range, ocean, and available oceans
