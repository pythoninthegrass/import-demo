#!/usr/bin/env python3

import csv
# import requests
from bs4 import BeautifulSoup
from datetime import timedelta
from decouple import config
from icecream import ic
from pathlib import Path

# TODO: rewrite `index.ts` as a python script
# # env vars
# API_URL = config('API_URL')
# API_KEY = config('API_KEY')

# glob for shiori_backup_*.html
backup = Path(".").glob('shiori_backup_*.html')

# get the latest html export
html_file = max(backup, key=lambda p: p.stat().st_mtime)


def parse_html(html):
    """Parse the shiori html backup"""

    with open(html, 'r') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')
    data = set()
    for dt in soup.find_all('dt'):
        try:
            href = dt.find('a').get('href')
            add_date = dt.find('a').get('add_date')
            last_modified = dt.find('a').get('last_modified')
            tags = dt.find_next_sibling('dd').get_text().split(',')
        except AttributeError:
            tags = None
        data.add((href, add_date, last_modified, tags))
    return data


def sort_data(filename, index=1):
    """Sort the data by timestamp"""

    # read data from csv
    with open(filename, 'r') as f:
        raw_csv = f.read().split('\n')

    # split each line into list of strings on each row
    raw_csv = [row.split(',') for row in raw_csv]

    # skip header
    raw_csv = raw_csv[1:]

    # sort by timestamp
    sorted_data = sorted(raw_csv, key=lambda x: x[2])

    # reverse order
    return sorted_data[::-1]


def export_csv(data, filename):
    """Export the data to csv"""

    with open(filename, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['url', 'status'])
        for row in data:
            writer.writerow([row[1], 'SUCCEEDED'])


def main():
    # TODO: test html file -> csv
    # parse html from shiori cli
    # data = parse_html(html_file)

    # TODO: add argparse/typer for tui
    # sql exported csv from shiori (postgres)
    prompt = input("Enter the filename: ")
    fn = prompt if prompt else "shiori_backup_20230806.csv"

    # validate file exists
    if not Path(fn).exists():
        print(f"File {fn} not found")
        raise FileNotFoundError

    # sort data
    data = sort_data(fn, index=1)

    # export the data to csv (overwrite)
    export_csv(data, "import.csv")


if __name__ == '__main__':
    main()
