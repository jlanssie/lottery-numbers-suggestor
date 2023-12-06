import os
import csv
import requests
from collections import Counter
import logging
from datetime import datetime

# Set up logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def fetch_url(base_url, year):
    url = f"{base_url}-{year}.csv"
    logger.debug("Fetching url: %s", url)
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logger.error(f"Error during request for {year}: {e}")
    return None

def get_most_common_numbers(file_path, numbers, bonus_numbers):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            next(file)
            for row in csv.reader(file, delimiter=';'):
                numbers.extend(row[1:-1])
                bonus_number = ''.join(row[-1:])
                bonus_numbers.append(bonus_number)
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {e}")

def get_most_common_numbers_paired_with_a_number(file_path, numbers_i):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            next(file)
            for row in csv.reader(file, delimiter=';'):
                if all(num in row for num in suggested_numbers):
                    find_and_extend(numbers_i, row, suggested_numbers)
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {e}")

def find_most_common(items, logger, name):
    counter = Counter(items)
    most_common_number = counter.most_common(1)[0][0]
    logger.debug(f"The most common {name} is: {most_common_number}")
    return most_common_number

def find_and_extend(items, row, suggested_numbers):
    items.extend(num for num in row[1:-1] if num not in set(suggested_numbers))

def combination_exists(suggested_numbers, data_directory):
    for file_name in os.listdir(data_directory):
        if file_name.endswith(".csv"):
            file_path = os.path.join(data_directory, file_name)
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    next(file)
                    for row in csv.reader(file, delimiter=';'):
                        if all(num in row for num in suggested_numbers):
                            logger.debug(f"Combination {suggested_numbers} exists in {file_path}")
                            return True
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {e}")
    return False


# Fetch data

base_url = "https://prdlnboppreportsst.blob.core.windows.net/legal-reports/lotto-gamedata-NL"
data_directory = "data"
os.makedirs(data_directory, exist_ok=True)

current_year = datetime.now().year

for year in range(2000, 2024):
    filename = os.path.join(data_directory, f"lotto-gamedata-NL-{year}.csv")
    if os.path.exists(filename) and year != current_year:
        logger.debug(f"Skipping {year} as data already exists.")
        continue

    response_text = fetch_url(base_url, year)

    if response_text is not None:
        with open(filename, "w", encoding="utf-8") as file:
            file.write(response_text)
            logger.debug(f"Content for {year} fetched from {base_url}-{year}.csv and saved to {filename}")
    else:
        logger.warning(f"Failed to fetch content for {year}")

# Process data

numbers = []
bonus_numbers = []

suggested_numbers = []

for file_name in os.listdir(data_directory):
    if file_name.endswith(".csv"):
        file_path = os.path.join(data_directory, file_name)
        get_most_common_numbers(file_path, numbers, bonus_numbers)

most_common_number = find_most_common(numbers, logger, "number")
suggested_numbers.append(most_common_number)

most_common_bonus_number = find_most_common(bonus_numbers, logger, "bonus number")

for i in range(1, 6):
    numbers_i = []

    for file_name in os.listdir(data_directory):
        if file_name.endswith(".csv"):
            file_path = os.path.join(data_directory, file_name)
            get_most_common_numbers_paired_with_a_number(file_path, numbers_i)

    most_common_number_i = find_most_common(numbers_i, logger, f"number paired with {suggested_numbers}")
    suggested_numbers.append(most_common_number_i)

    if i == 6:
        if combination_exists(suggested_numbers, data_directory): 
            logger.info("Combination", combination, "exists.")
            #TODO propose new combination

print("Suggested numbers:", ', '.join(map(str, suggested_numbers)), "\nSuggested bonus number:", most_common_bonus_number)



