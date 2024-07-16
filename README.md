# Popular Repositories Analysis

Analyzing popular GitHub repositories for UVP project.

## About

TODO

## Installation

This project requires Python 3.10 or later and [Poetry](https://python-poetry.org/) dependency manager 1.8.0 or later.

You can clone this repository and install the required dependencies using Poetry:

```bash
git clone https://github.com/filips123/PopularRepositoriesAnalysis.git
cd PopularRepositoriesAnalysis
poetry install
```

## Scraping Data

Before running the API scrapers, you need to create [a read-only token](https://github.com/settings/tokens/new?description=Popular%20Repositories%20Analysis) and store it inside the `scraper/auth.txt` file.

To collect all the required data, you can run the API scrapers with the following commands:

```shell
# Repositories Scraper
python scraper/main.py repositories stars # Top repositories by stars
python scraper/main.py repositories forks # Top repositories by forks

# Users Scraper
python scraper/main.py users followers # Top users by forks
python scraper/main.py users repositories # Top users by repositories
```

By default, 1000 results will be fetched for each query.
Each of the commands will take approximately 10–30 minutes to complete.
The collected data will be stored inside the `data` directory.

There is also an additional HTML scraper, which can collect similar data about a specific repository as the API scraper, but by downloading and parsing HTML.
However, this scraper is less reliable and cannot collect all data, so it is recommended to use the API scrapers instead.

The HTML scraper can be run with the following command:

```shell
python scrapers/manual.py YOUR-REPOSITORY-URL
```

## Existing Data

The repository already provides the following lists:

* Top 5000 repositories by stars, collected on 2024-07-14.
* Top 5000 repositories by forks, collected on 2024-07-14.
* Top 5000 users by followers, collected on 2024-07-14.
* ~~Top 5000 users by repositories, collected on 2024-07-14.~~ *Incorrect due to a GitHub API bug.*
