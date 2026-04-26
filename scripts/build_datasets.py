from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATASETS_DIR = BASE_DIR / "datasets"
APP_DATA_DIR = BASE_DIR / "app" / "data"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def write_json(path: Path, payload: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2, ensure_ascii=False)
        file.write("\n")


def parse_float(value: str) -> float | None:
    cleaned = value.strip()
    if not cleaned:
        return None
    return float(cleaned)


def parse_int(value: str) -> int | None:
    cleaned = value.strip()
    if not cleaned:
        return None
    return int(cleaned)


def parse_iso_date(value: str) -> str:
    return datetime.strptime(value.strip(), "%m/%d/%Y %I:%M:%S %p").date().isoformat()


def normalize_text(value: str) -> str | None:
    cleaned = value.strip()
    return cleaned or None


def build_ocean_warming() -> list[dict]:
    rows = read_csv(DATASETS_DIR / "ocean_warming.csv")

    return [
        {
            # The source stores annual values as midpoints like 1957.5.
            # We expose an integer year for a cleaner API and keep the original value too.
            "year": int(parse_float(row["YEAR"])),
            "source_year_midpoint": parse_float(row["YEAR"]),
            "world_ohc_zj": parse_float(row["WO"]),
            "world_ohc_se_zj": parse_float(row["WOse"]),
            "northern_hemisphere_ohc_zj": parse_float(row["NH"]),
            "northern_hemisphere_ohc_se_zj": parse_float(row["NHse"]),
            "southern_hemisphere_ohc_zj": parse_float(row["SH"]),
            "southern_hemisphere_ohc_se_zj": parse_float(row["SHse"]),
        }
        for row in rows
    ]


def build_ocean_acidification() -> list[dict]:
    rows = read_csv(DATASETS_DIR / "ocean_acidification.csv")

    return [
        {
            "date": row["Date"].strip(),
            "location": normalize_text(row["Location"]),
            "latitude": parse_float(row["Latitude"]),
            "longitude": parse_float(row["Longitude"]),
            "sst_c": parse_float(row["SST (°C)"]),
            "ph_level": parse_float(row["pH Level"]),
            "bleaching_severity": normalize_text(row["Bleaching Severity"]),
            "species_observed": parse_int(row["Species Observed"]),
            "marine_heatwave": row["Marine Heatwave"].strip().lower() == "true",
        }
        for row in rows
    ]


def build_commercial_whaling() -> list[dict]:
    rows = read_csv(DATASETS_DIR / "whale_catch.csv")

    return [
        {
            "hemisphere": row["Entity"].strip(),
            "code": row["Code"].strip(),
            "year": parse_int(row["Year"]),
            "all_whale_species": parse_int(row["All whale species"]),
            "brydes_whale": parse_int(row["Bryde's whale"]),
            "gray_whale": parse_int(row["Gray whale"]),
            "minke_whale": parse_int(row["Minke whale"]),
            "sei_whale": parse_int(row["Sei whale"]),
            "unspecified_other_species": parse_int(row["Unspecified/other species"]),
            "blue_whale": parse_int(row["Blue whale"]),
            "fin_whale": parse_int(row["Fin whale"]),
            "humpback_whale": parse_int(row["Humpback whale"]),
            "right_whale": parse_int(row["Right whale"]),
            "sperm_whale": parse_int(row["Sperm whale"]),
        }
        for row in rows
        if row["Entity"].strip() == "Southern Hemisphere"
    ]


def build_marine_microplastics() -> list[dict]:
    rows = read_csv(DATASETS_DIR / "marine_microplastics.csv")
    cleaned_rows: list[dict] = []

    for row in rows:
        latitude = parse_float(row["Latitude"])
        longitude = parse_float(row["Longitude"])
        if latitude is None or longitude is None:
            continue

        if latitude >= 0:
            continue

        if row["Unit"].strip() != "pieces/m3":
            continue

        cleaned_rows.append(
            {
                "ocean": normalize_text(row["Oceans"]),
                "region": normalize_text(row["Regions"]),
                "subregion": normalize_text(row["SubRegions"]),
                "sampling_method": normalize_text(row["Sampling Method"]),
                "measurement_pieces_m3": parse_float(row["Measurement"]),
                "unit": row["Unit"].strip(),
                "density_range": normalize_text(row["Density Range"]),
                "density_class": normalize_text(row["Density Class"]),
                "short_reference": normalize_text(row["Short Reference"]),
                "doi": normalize_text(row["DOI"]),
                "organization": normalize_text(row["Organization"]),
                "keywords": normalize_text(row["Keywords"]),
                "accession_number": normalize_text(row["Accession Number"]),
                "accession_link": normalize_text(row["Accession Link"]),
                "latitude": latitude,
                "longitude": longitude,
                "date": parse_iso_date(row["Date"]),
            }
        )

    return cleaned_rows


def main() -> None:
    datasets = {
        "ocean_warming.json": build_ocean_warming(),
        "ocean_acidification.json": build_ocean_acidification(),
        "commercial_whaling.json": build_commercial_whaling(),
        "marine_microplastics.json": build_marine_microplastics(),
    }

    for filename, payload in datasets.items():
        write_json(APP_DATA_DIR / filename, payload)
        print(f"Wrote {filename}: {len(payload)} records")


if __name__ == "__main__":
    main()
