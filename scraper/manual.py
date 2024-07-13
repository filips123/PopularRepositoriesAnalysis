import sys
from dataclasses import dataclass

import orjson
import requests
from bs4 import BeautifulSoup


# mypy: ignore-errors


@dataclass
class Repository:
    # == Basic Properties

    owner: str
    """The repository owner."""

    name: str
    """The repository name."""

    url: str
    """The repository URL."""

    default_branch: str
    """The repository default branch."""

    # == Social Properties

    # description: str | None
    """The repository description, if set."""

    # homepage: str | None
    """The repository homepage, if set."""

    # topics: list[str]
    """The repository topics."""

    # == Counts Properties

    stargazers_count: str
    """The number of repository stargazers."""

    forks_count: str
    """The number of repository forks."""

    open_issues_count: str
    """The number of open repository issues."""

    open_prs_count: str
    """The number of open repository pull requests."""

    open_projects_count: str
    """The number of open repository projects."""

    releases_count: str
    """The number of repository releases."""

    packages_count: str
    """The number of repository packages."""

    contributors_count: str
    """The number of repository contributors."""


def get_repository_details(url: str) -> Repository:
    """Gets the repository details by downloading and parsing the repository page."""

    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, features="lxml")

    # Get the repository properties from the header
    header = soup.find("div", {"id": "repository-container-header"})
    owner = header.find("span", {"class": "author"}).text.strip()
    name = header.find("strong", {"itemprop": "name"}).text.strip()

    # Get the repository properties from the sidebar
    # These selectors are not reliable, so they are disabled for now
    # sidebar = soup.find("div", {"class": "BorderGrid-cell"}).find("div")
    # description = sidebar.select_one(":nth-child(2)").text.strip()
    # homepage = sidebar.select_one(":nth-child(3)").find("a", href=True)["href"]
    # topics = [topic.text.strip() for topic in sidebar.select_one(":nth-child(5)").find_all("a")]

    # Get the default repository branch
    default_branch = soup.find("button", {"id": "branch-picker-repos-header-ref-selector"}).text.strip()

    # Get the base repository counters
    stargazers_count = soup.find("span", {"id": "repo-stars-counter-star"})["title"].replace(",", "")
    forks_count = soup.find("span", {"id": "repo-network-counter"})["title"].replace(",", "")
    open_issues_count = soup.find("span", {"id": "issues-repo-tab-count"})["title"].replace(",", "")
    open_prs_count = soup.find("span", {"id": "pull-requests-repo-tab-count"})["title"].replace(",", "")
    open_projects_count = soup.find("span", {"id": "projects-repo-tab-count"})["title"].replace(",", "")

    # Get the releases count from the counter in the sidebar
    releases_count = (
        (soup.select_one("a[href*=releases] .Counter")["title"].replace(",", ""))
        if soup.select_one("a[href*=releases] .Counter")
        else "0"
    )

    # Get the packages count from the counter in the sidebar
    packages_count = (
        (soup.select_one("a[href*=packages] .Counter")["title"].replace(",", ""))
        if soup.select_one("a[href*=packages] .Counter")
        else "0"
    )

    # Get the contributors count from the counter in the sidebar
    contributors_count = (
        (soup.select_one("a[href$=graphs\\/contributors] .Counter")["title"].replace(",", ""))
        if soup.select_one("a[href$=graphs\\/contributors] .Counter")
        else "0"
    )

    return Repository(
        # == Basic Properties
        owner=owner,
        name=name,
        url=url,
        default_branch=default_branch,
        # == Social Properties
        # description=description,
        # homepage=homepage,
        # topics=topics,
        # == Counts Properties
        stargazers_count=stargazers_count,
        forks_count=forks_count,
        open_issues_count=open_issues_count,
        open_prs_count=open_prs_count,
        open_projects_count=open_projects_count,
        releases_count=releases_count,
        packages_count=packages_count,
        contributors_count=contributors_count,
    )


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python scrapers/manual.py YOUR-REPOSITORY-URL", file=sys.stderr)
        sys.exit(1)

    url = sys.argv[1]
    details = get_repository_details(url)
    print(orjson.dumps(details, option=orjson.OPT_INDENT_2).decode())


if __name__ == "__main__":
    main()
