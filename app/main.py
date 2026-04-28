from __future__ import annotations

import json
from datetime import date as date_type
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "app" / "data"
LOCAL_FRONTEND_ORIGIN_REGEX = r"^https?://(localhost|127\.0\.0\.1|\[::1\])(:\d+)?$"

DATASET_FILES = {
    "/ocean-warming": "ocean_warming.json",
    "/ocean-acidification": "ocean_acidification.json",
    "/commercial-whaling": "commercial_whaling.json",
    "/marine-microplastics": "marine_microplastics.json",
}

COMMERCIAL_WHALING_SPECIES = {
    "all_whale_species",
    "brydes_whale",
    "gray_whale",
    "minke_whale",
    "sei_whale",
    "unspecified_other_species",
    "blue_whale",
    "fin_whale",
    "humpback_whale",
    "right_whale",
    "sperm_whale",
}

app = FastAPI(title="Whale Migration API")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=LOCAL_FRONTEND_ORIGIN_REGEX,
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


def load_dataset(filename: str) -> list[dict]:
    file_path = DATA_DIR / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Dataset not found: {filename}")

    try:
        with file_path.open("r", encoding="utf-8") as file:
            payload = json.load(file)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"The file {filename} does not contain valid JSON.",
        ) from exc

    if not isinstance(payload, list):
        raise HTTPException(
            status_code=500,
            detail=f"The file {filename} must contain a JSON array.",
        )

    return payload


def load_ocean_warming_dataset() -> list[dict]:
    return load_dataset(DATASET_FILES["/ocean-warming"])


def find_ocean_warming_record(year: int) -> dict:
    records = load_ocean_warming_dataset()

    for record in records:
        if record.get("year") == year:
            return record

    raise HTTPException(status_code=404, detail=f"No ocean warming record found for year {year}.")


def load_commercial_whaling_dataset() -> list[dict]:
    return load_dataset(DATASET_FILES["/commercial-whaling"])


def find_commercial_whaling_record(year: int) -> dict:
    records = load_commercial_whaling_dataset()

    for record in records:
        if record.get("year") == year:
            return record

    raise HTTPException(status_code=404, detail=f"No commercial whaling record found for year {year}.")


def validate_commercial_whaling_species(species: str) -> str:
    if species not in COMMERCIAL_WHALING_SPECIES:
        supported_species = ", ".join(sorted(COMMERCIAL_WHALING_SPECIES))
        raise HTTPException(
            status_code=404,
            detail=f"Unsupported species '{species}'. Supported values: {supported_species}.",
        )

    return species


def build_commercial_whaling_species_response(records: list[dict], species: str) -> list[dict]:
    return [
        {
            "year": record["year"],
            "hemisphere": record["hemisphere"],
            "species": species,
            "catch_count": record[species],
        }
        for record in records
    ]


def load_ocean_acidification_dataset() -> list[dict]:
    return load_dataset(DATASET_FILES["/ocean-acidification"])


def load_marine_microplastics_dataset() -> list[dict]:
    return load_dataset(DATASET_FILES["/marine-microplastics"])


def validate_iso_date(value: str, field_name: str) -> str:
    try:
        return date_type.fromisoformat(value).isoformat()
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} must use YYYY-MM-DD format.",
        ) from exc


def apply_limit(records: list[dict], limit: int | None) -> list[dict]:
    if limit is None:
        return records
    return records[:limit]


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "Whale Migration API",
        "docs": "/docs",
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/datasets")
def datasets() -> list[str]:
    return list(DATASET_FILES.keys())


@app.get("/commercial-whaling")
def commercial_whaling() -> list[dict]:
    return load_commercial_whaling_dataset()


@app.get("/commercial-whaling/range")
def commercial_whaling_range(
    start_year: int = Query(..., description="Start year of the requested range"),
    end_year: int = Query(..., description="End year of the requested range"),
) -> list[dict]:
    if start_year > end_year:
        raise HTTPException(status_code=400, detail="start_year cannot be greater than end_year.")

    records = load_commercial_whaling_dataset()
    filtered_records = [
        record for record in records if start_year <= record["year"] <= end_year
    ]

    if not filtered_records:
        raise HTTPException(
            status_code=404,
            detail=f"No commercial whaling records found between {start_year} and {end_year}.",
        )

    return filtered_records


@app.get("/commercial-whaling/species/{species}")
def commercial_whaling_by_species(species: str) -> list[dict]:
    species_name = validate_commercial_whaling_species(species)
    records = load_commercial_whaling_dataset()
    return build_commercial_whaling_species_response(records, species_name)


@app.get("/commercial-whaling/species/{species}/range")
def commercial_whaling_species_range(
    species: str,
    start_year: int = Query(..., description="Start year of the requested range"),
    end_year: int = Query(..., description="End year of the requested range"),
) -> list[dict]:
    if start_year > end_year:
        raise HTTPException(status_code=400, detail="start_year cannot be greater than end_year.")

    species_name = validate_commercial_whaling_species(species)
    records = load_commercial_whaling_dataset()
    filtered_records = [
        record for record in records if start_year <= record["year"] <= end_year
    ]

    if not filtered_records:
        raise HTTPException(
            status_code=404,
            detail=f"No commercial whaling records found between {start_year} and {end_year}.",
        )

    return build_commercial_whaling_species_response(filtered_records, species_name)


@app.get("/commercial-whaling/{year}")
def commercial_whaling_by_year(year: int) -> dict:
    return find_commercial_whaling_record(year)


@app.get("/ocean-warming")
def ocean_warming() -> list[dict]:
    return load_dataset(DATASET_FILES["/ocean-warming"])


@app.get("/ocean-warming/range")
def ocean_warming_range(
    start_year: int = Query(..., description="Start year of the requested range"),
    end_year: int = Query(..., description="End year of the requested range"),
) -> list[dict]:
    if start_year > end_year:
        raise HTTPException(status_code=400, detail="start_year cannot be greater than end_year.")

    records = load_ocean_warming_dataset()
    filtered_records = [
        record for record in records if start_year <= record["year"] <= end_year
    ]

    if not filtered_records:
        raise HTTPException(
            status_code=404,
            detail=f"No records found between {start_year} and {end_year}.",
        )

    return filtered_records


@app.get("/ocean-warming/{year}")
def ocean_warming_by_year(year: int) -> dict:
    return find_ocean_warming_record(year)


@app.get("/marine-microplastics")
def marine_microplastics(
    limit: int | None = Query(None, ge=1, description="Maximum number of records to return"),
) -> list[dict]:
    records = load_marine_microplastics_dataset()
    return apply_limit(records, limit)


@app.get("/marine-microplastics/oceans")
def marine_microplastics_oceans() -> list[str]:
    records = load_marine_microplastics_dataset()
    return sorted({record["ocean"] for record in records if record.get("ocean")})


@app.get("/marine-microplastics/range")
def marine_microplastics_range(
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    limit: int | None = Query(None, ge=1, description="Maximum number of records to return"),
) -> list[dict]:
    validated_start_date = validate_iso_date(start_date, "start_date")
    validated_end_date = validate_iso_date(end_date, "end_date")

    if validated_start_date > validated_end_date:
        raise HTTPException(status_code=400, detail="start_date cannot be greater than end_date.")

    records = load_marine_microplastics_dataset()
    filtered_records = [
        record
        for record in records
        if validated_start_date <= record["date"] <= validated_end_date
    ]

    if not filtered_records:
        raise HTTPException(
            status_code=404,
            detail=f"No marine microplastics records found between {validated_start_date} and {validated_end_date}.",
        )

    return apply_limit(filtered_records, limit)


@app.get("/marine-microplastics/date/{record_date}")
def marine_microplastics_by_date(record_date: str) -> list[dict]:
    validated_record_date = validate_iso_date(record_date, "record_date")
    records = load_marine_microplastics_dataset()
    filtered_records = [record for record in records if record["date"] == validated_record_date]

    if not filtered_records:
        raise HTTPException(
            status_code=404,
            detail=f"No marine microplastics records found for {validated_record_date}.",
        )

    return filtered_records


@app.get("/marine-microplastics/ocean/{ocean}")
def marine_microplastics_by_ocean(
    ocean: str,
    limit: int | None = Query(None, ge=1, description="Maximum number of records to return"),
) -> list[dict]:
    records = load_marine_microplastics_dataset()
    filtered_records = [
        record
        for record in records
        if record.get("ocean", "").casefold() == ocean.casefold()
    ]

    if not filtered_records:
        raise HTTPException(
            status_code=404,
            detail=f"No marine microplastics records found for ocean '{ocean}'.",
        )

    return apply_limit(filtered_records, limit)


@app.get("/ocean-acidification")
def ocean_acidification(
    limit: int | None = Query(None, ge=1, description="Maximum number of records to return"),
) -> list[dict]:
    records = load_ocean_acidification_dataset()
    return apply_limit(records, limit)


@app.get("/ocean-acidification/locations")
def ocean_acidification_locations() -> list[str]:
    records = load_ocean_acidification_dataset()
    return sorted({record["location"] for record in records if record.get("location")})


@app.get("/ocean-acidification/range")
def ocean_acidification_range(
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    limit: int | None = Query(None, ge=1, description="Maximum number of records to return"),
) -> list[dict]:
    validated_start_date = validate_iso_date(start_date, "start_date")
    validated_end_date = validate_iso_date(end_date, "end_date")

    if validated_start_date > validated_end_date:
        raise HTTPException(status_code=400, detail="start_date cannot be greater than end_date.")

    records = load_ocean_acidification_dataset()
    filtered_records = [
        record
        for record in records
        if validated_start_date <= record["date"] <= validated_end_date
    ]

    if not filtered_records:
        raise HTTPException(
            status_code=404,
            detail=f"No ocean acidification records found between {validated_start_date} and {validated_end_date}.",
        )

    return apply_limit(filtered_records, limit)


@app.get("/ocean-acidification/date/{record_date}")
def ocean_acidification_by_date(record_date: str) -> list[dict]:
    validated_record_date = validate_iso_date(record_date, "record_date")
    records = load_ocean_acidification_dataset()
    filtered_records = [record for record in records if record["date"] == validated_record_date]

    if not filtered_records:
        raise HTTPException(
            status_code=404,
            detail=f"No ocean acidification records found for {validated_record_date}.",
        )

    return filtered_records


@app.get("/ocean-acidification/location/{location}")
def ocean_acidification_by_location(
    location: str,
    limit: int | None = Query(None, ge=1, description="Maximum number of records to return"),
) -> list[dict]:
    records = load_ocean_acidification_dataset()
    filtered_records = [
        record
        for record in records
        if record.get("location", "").casefold() == location.casefold()
    ]

    if not filtered_records:
        raise HTTPException(
            status_code=404,
            detail=f"No ocean acidification records found for location '{location}'.",
        )

    return apply_limit(filtered_records, limit)
