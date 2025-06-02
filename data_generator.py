#!/usr/bin/env python3

import random
from datetime import datetime, timedelta
from pathlib import Path

import joblib
import polars as pl
import tqdm

# Some examples of descriptive adjectives
ADJECTIVES = [
    "Majestic",
    "Grand",
    "Marvelous",
    "Glorious",
    "Fabulous",
    "Radiant",
    "Mighty",
    "Magnificent",
    "Royal",
    "Vibrant",
    "Shimmering",
    "Gorgeous",
    "Splendid",
    "Luminous",
    "Regal",
    "Noble",
    "Enchanted",
    "Ethereal",
    "Velvet",
    "Brilliant",
    "Opulent",
    "Miraculous",
    "Astounding",
    "Mystic",
    "Resplendent",
    "Dazzling",
    "Incredible",
    "Exquisite",
    "Delightful",
    "Breathtaking",
    "Serene",
    "Exotic",
    "Fantastic",
    "Exquisite",
    "Marvelous",
    "Prodigious",
    "Glittering",
    "Pulsing",
    "Electric",
    "Velvety",
]

# Some examples of fish species names
FISH_TYPES = [
    "Betta",
    "Discus",
    "Guppy",
    "Goldfish",
    "Tetra",
    "Swordtail",
    "Cichlid",
    "Koi",
    "Molly",
    "Angelfish",
    "Catfish",
    "Zebrafish",
    "Platy",
    "Barb",
    "Rainbowfish",
    "Loach",
    "Oscar",
    "Ram",
    "Endler",
    "Rasbora",
    "Danio",
    "Puffer",
    "Sharkminnow",
    "Arowana",
    "Pollyfish",
    "Clownfish",
    "Tang",
    "Darter",
    "Sunfish",
    "Basslet",
    "Seahorse",
    "Pipefish",
    "Killifish",
]


def generate_species_list(num_species=500):
    """
    Creates a set of 'num_species' fish species, each formed by
    combining a random adjective with a random fish type,
    e.g., "MajesticBetta" or "FabulousDiscus".

    We ensure no duplicates by storing them in a set until we reach
    the desired quantity, or exhaust combinations (whichever comes first).
    """
    all_combos = set()
    max_attempts = num_species * 5  # safeguard for random loops

    while len(all_combos) < num_species and max_attempts > 0:
        adj = random.choice(ADJECTIVES)
        fish = random.choice(FISH_TYPES)
        combo = f"{adj}{fish}"
        all_combos.add(combo)
        max_attempts -= 1

    # Convert set to a list and return
    return list(all_combos)


def generate_tank_info(num_tanks=20, species_list=None):
    """
    Creates tank_info data with columns:
      tank_id, fish_species
    - tank_id in [1..num_tanks]
    - fish_species randomly chosen from 'species_list'
    """
    if species_list is None:
        # Default to 500 generated species
        species_list = generate_species_list(500)

    rows = []
    for tank_id in range(1, num_tanks + 1):
        fish_species = random.sample(species_list, k=5)
        capacity = random.randint(1000, 1800)
        rows.append({"tank_id": tank_id, "fish_species": ",".join(fish_species), "capacity_liters": capacity})
    return rows


def generate_sensor_data(num_tanks=5, num_readings=20, start_date="2025-01-01"):
    """
    Creates sensor readings with columns:
      tank_id, time, pH, temp, capacity_liters

    - Randomly picks from 1..num_tanks for tank_id.
    - Time is spread around a given start date with random offsets.
    - pH is in a range of ~6.5 to 8.0
    - Temp is in a range of ~22 to 28
    - capacity_liters is from 200 to 1000
    Returns a list of dict rows.
    """
    base_date = datetime.strptime(start_date, "%Y-%m-%d")

    def generate_sensor_row():
        tank_id = random.randint(1, num_tanks)
        # Generate a random offset (in hours or days) from base_date
        offset_days = random.randint(0, 10)  # up to 10 days after
        offset_hours = random.randint(0, 23)
        timestamp = base_date + timedelta(days=offset_days, hours=offset_hours)

        pH = round(random.uniform(6.5, 8.0), 2)
        temp = round(random.uniform(22.0, 28.0), 2)
        quantity = random.randint(200, 1000)
        quantity_none = random.randint(1, 10) == 2
        if quantity_none:
            quantity = None

        return {
            "tank_id": tank_id,
            "time": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "pH": pH,
            "temp": temp,
            "quantity_liters": quantity,
        }

    rows = joblib.Parallel(n_jobs=-1)(
        joblib.delayed(generate_sensor_row)() for _ in tqdm.tqdm(range(num_readings), desc="Generating sensor data")
    )

    return rows


def main():
    # For reproducibility, you can fix the random seed:
    # random.seed(42)

    NUM_TANKS = 100
    NUM_READINGS = 100_000

    # Create a big list of random fish species names
    species_pool = generate_species_list(num_species=500)

    # Create 'tank_info.tsv'
    tank_info = generate_tank_info(num_tanks=NUM_TANKS, species_list=species_pool)
    sensors = generate_sensor_data(num_tanks=NUM_TANKS, num_readings=NUM_READINGS, start_date="2025-01-01")

    output_path = Path("data")
    output_path.mkdir(exist_ok=True)

    # Write tank_info.tsv
    pl.DataFrame(tank_info, schema=["tank_id", "fish_species", "capacity_liters"]).write_csv(
        output_path / "full_tank_info.tsv", separator="\t"
    )

    # Write sensors.tsv
    pl.DataFrame(sensors, schema=["tank_id", "time", "pH", "temp", "quantity_liters"]).write_csv(
        output_path / "full_sensors.tsv", separator="\t"
    )

    print(f"Generated 'tank_info.tsv' (with {len(tank_info)} rows) and 'sensors.tsv' (with {len(sensors)} rows).")


if __name__ == "__main__":
    main()
