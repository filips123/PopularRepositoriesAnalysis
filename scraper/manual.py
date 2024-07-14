import sys
from dataclasses import dataclass

import orjson
import requests
from bs4 import BeautifulSoup, Tag


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

    license: str | None
    """The repository license, if detected."""

    languages: dict[str, int]
    """The all repository languages with percentages."""

    # == Social Properties

    description: str | None
    """The repository description, if set."""

    homepage: str | None
    """The repository homepage, if set."""

    topics: list[str]
    """The repository topics."""

    # == Counts Properties

    stargazers_count: int
    """The number of repository stargazers."""

    watchers_count: int
    """The number of repository watchers."""

    forks_count: int
    """The number of repository forks."""

    open_issues_count: int
    """The number of open repository issues."""

    open_prs_count: int
    """The number of open repository pull requests."""

    open_projects_count: int
    """The number of open repository projects."""

    commits_count: int
    """The number of repository commits to default branch."""

    releases_count: int
    """The number of repository releases."""

    packages_count: int
    """The number of repository packages."""

    contributors_count: int
    """The number of repository contributors."""


def parse_number(text: str) -> int:
    """Parses the number from text format into integer."""

    # The number may be limited to something like 5k+
    text = text.replace("+", "")

    if "k" in text:
        # Remove "k" and convert to float to handle decimals, then multiply by 1000
        return int(float(text.replace("k", "")) * 1000)
    else:
        # Remove commas as thousands separators and convert to integer
        return int(text.replace(",", ""))


def get_number_from_counter(element: Tag | None) -> int:
    """Gets the number from the counter, returns 0 if it does not exist."""

    if not element:
        return 0

    return parse_number(element["title"])


def get_repository_details(url: str) -> Repository:
    """Gets the repository details by downloading and parsing the repository page."""

    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, features="lxml")

    # Get the repository properties from the header
    header = soup.find("div", {"id": "repository-container-header"})
    owner = header.find("span", {"class": "author"}).text.strip()
    name = header.find("strong", {"itemprop": "name"}).text.strip()

    # Get the repository sidebar
    sidebar = soup.find("div", {"class": "BorderGrid-cell"}).find("div")

    # Get the repository description from the sidebar
    # If the description is not set, the text is displayed in italic
    if (description_box := sidebar.select_one(":nth-child(2)")) and (
        "text-italic" not in description_box["class"]
    ):
        description = description_box.text.strip()
    else:
        description = None

    # Get the repository homepage from the sidebar
    if homepage_icon := sidebar.find("svg", {"class": "octicon-link"}):
        homepage_box = homepage_icon.parent
        homepage = homepage_box.find("a", href=True)["href"]
    else:
        homepage = None

    # Get the repository topics from the sidebar
    if topics_title := sidebar.find("h3", string="Topics"):
        topics_box = topics_title.find_next_sibling("div")
        topics = [topic.text.strip() for topic in topics_box.find_all("a")]
    else:
        topics = []

    # Get the default repository branch
    default_branch = soup.find("button", {"id": "branch-picker-repos-header-ref-selector"}).text.strip()

    # Get the repository license from the files navigation
    files = soup.find("nav", {"aria-label": "Repository files"})
    if files and files.select_one('span:-soup-contains("License")'):
        # There is a license, but we could not classify it
        license = "NOASSERTION"
    elif files and files.select_one('span:-soup-contains(" license")'):
        # There is a license, and we could classify it
        license = files.select_one('span:-soup-contains(" license")').text.split(" ")[0]
    else:
        # There is no license detected
        license = None

    # Get the repository languages from the sidebar
    languages = {}
    if languages_title := soup.find("h2", string="Languages", attrs={"class": "h4"}):
        languages_box = languages_title.parent
        languages_list = languages_box.find("ul")
        for language_item in languages_list.find_all("li"):
            language_name, language_percentage = language_item.text.strip().split("\n")
            languages[language_name] = language_percentage

    # Get the base repository counters
    stargazers_count = get_number_from_counter(soup.find("span", {"id": "repo-stars-counter-star"}))
    forks_count = get_number_from_counter(soup.find("span", {"id": "repo-network-counter"}))
    open_issues_count = get_number_from_counter(soup.find("span", {"id": "issues-repo-tab-count"}))
    open_prs_count = get_number_from_counter(soup.find("span", {"id": "pull-requests-repo-tab-count"}))
    open_projects_count = get_number_from_counter(soup.find("span", {"id": "projects-repo-tab-count"}))

    # Get the watchers count from the sidebar
    watchers_count = parse_number(sidebar.select_one('a:-soup-contains(" watching")').text.split(" ")[0])

    # Get the commits count from the commits box
    commits_box = soup.find("table", {"aria-labelledby": "folders-and-files"})
    commits_count = parse_number(commits_box.select_one('span:-soup-contains(" Commits")').text.split(" ")[0])

    # Get the releases count from the counter in the sidebar
    releases_count = get_number_from_counter(soup.select_one("a[href*=releases] .Counter"))

    # Get the packages count from the counter in the sidebar
    packages_count = get_number_from_counter(soup.select_one("a[href*=packages] .Counter"))

    # Get the contributors count from the counter in the sidebar
    contributors_count = get_number_from_counter(soup.select_one("a[href$=graphs\\/contributors] .Counter"))

    return Repository(
        # == Basic Properties
        owner=owner,
        name=name,
        url=url,
        default_branch=default_branch,
        license=license,
        languages=languages,
        # == Social Properties
        description=description,
        homepage=homepage,
        topics=topics,
        # == Counts Properties
        stargazers_count=stargazers_count,
        watchers_count=watchers_count,
        forks_count=forks_count,
        open_issues_count=open_issues_count,
        open_prs_count=open_prs_count,
        open_projects_count=open_projects_count,
        commits_count=commits_count,
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
