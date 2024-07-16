# Popular Repositories Analysis

Analyzing popular GitHub repositories for *Uvod v programiranje* (UVP) project at FMF UL.

## About

The aim of this project is to analyze the most popular GitHub repositories.
This has been done by downloading a list of top 5000 repositories and users using the GitHub search API and downloading additional properties about each repository and user.
These properties include the owner, name, description, topics, languages, stars, etc. for repositories, and name, homepage, company, location, etc. for users.
All repositories and users have then been analyzed in Jupyter Notebooks using the Pandas library.

If you want to quickly view the analysis, [check the instructions below](#viewing-analysis).

## Installation

This project requires Python 3.10 or later and [Poetry](https://python-poetry.org/) dependency manager 1.8.0 or later.

You can clone this repository and install the required dependencies using Poetry:

```shell
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

## Viewing Analysis

The analysis has been done using Jupyter Notebooks in the [`analysis`](analysis) directory.
It is recommended to clone the repository and view them locally, as GitHub cannot properly render all notebook features.
Alternatively, you can view them online using nbviewer:

* [Analysis of top GitHub repositories](https://nbviewer.org/github/filips123/PopularRepositoriesAnalysis/blob/main/analysis/repositories.ipynb)
* [Analysis of top GitHub users](https://nbviewer.org/github/filips123/PopularRepositoriesAnalysis/blob/main/analysis/users.ipynb)
