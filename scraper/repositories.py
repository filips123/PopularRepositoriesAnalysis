from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from github import Github
from tqdm import tqdm

CHUNK_MARGIN = 50
CHUNK_SIZE = float("inf")


@dataclass
class Repository:
    # == Basic Properties

    id: int
    """The internal repository ID."""

    owner: str
    """The repository owner."""

    name: str
    """The repository name."""

    url: str
    """The repository URL."""

    size: int
    """The repository size."""

    default_branch: str
    """The repository default branch."""

    license: str | None
    """The repository license, if set."""

    language: str | None
    """The main repository language, if detected."""

    languages: dict[str, int]
    """The all repository languages, if detected."""

    # == Social Properties

    description: str | None
    """The repository description, if set."""

    homepage: str | None
    """The repository homepage, if set."""

    topics: list[str]
    """The repository topics."""

    # == Dates Properties

    created_at: datetime
    """The time the repository was created."""

    updated_at: datetime
    """The time the repository was last updated."""

    pushed_at: datetime
    """The time the repository was last pushed to."""

    # == Counts Properties

    stargazers_count: int
    """The number of repository stargazers."""

    watchers_count: int
    """The number of repository watchers."""

    forks_count: int
    """The number of repository forks."""

    open_issues_count: int
    """The number of open repository issues and pull requests."""

    # Features Properties

    has_issues: bool
    """Whether the repository has issues enabled."""

    has_discussions: bool
    """Whether the repository has discussions enabled."""

    has_wiki: bool
    """Whether the repository has wiki enabled."""

    has_pages: bool
    """Whether the repository has pages enabled."""

    has_projects: bool
    """Whether the repository has projects enabled."""

    has_downloads: bool
    """Whether the repository has downloads enabled (feature deprecated since 2012)."""

    # Type Properties

    is_fork: bool
    """Whether the repository is a fork."""

    is_template: bool
    """Whether the repository is a template."""

    is_archived: bool
    """Whether the repository is archived."""


def find_max_value(github: Github, order: Literal["stars", "forks"]) -> int:
    """Find the maximum number of stars/forks any repository has."""

    # We start the query from 1000 to make it slightly faster
    query = github.search_repositories(query=f"{order}:>1000", sort=order, order="desc")

    match order:
        case "stars":
            return int(query[0].stargazers_count)
        case "forks":
            return int(query[0].forks_count)


def get_top_repositories(
    github: Github,
    order: Literal["stars", "forks"],
    amount: int,
) -> list[Repository]:
    """Get the top repositories by the specified order."""

    # The maximum number of stars/forks any repository has
    previous = find_max_value(github, order)

    repositories: dict[int, Repository] = {}

    with tqdm(total=amount) as pbar:
        # The search API limits the maximum number of results to 1000
        # To get more results, we need to query the API in smaller chunks

        while len(repositories) < amount:
            # We increase this slightly to account for possible increases
            chunk_max = previous + CHUNK_MARGIN
            chunk_min = max(chunk_max - CHUNK_SIZE, 1)

            # Set the progress bar description
            pbar.set_description(f"Chunk {chunk_min}-{chunk_max}")

            # Query all repositories in the chunk range
            query = github.search_repositories(
                f"{order}:{chunk_min}..{chunk_max}",
                sort=order,
                order="desc",
            )

            for repository in query:
                # Add the repository to the result
                repositories[repository.id] = Repository(
                    # == Basic Properties
                    id=repository.id,
                    owner=repository.owner.login,
                    name=repository.name,
                    url=repository.html_url,
                    size=repository.size,
                    default_branch=repository.default_branch,
                    license=repository.license.spdx_id if repository.license else None,
                    language=repository.language or None,
                    languages=repository.get_languages(),
                    # == Social Properties
                    description=repository.description or None,
                    homepage=repository.homepage or None,
                    topics=repository.topics,
                    # == Dates Properties
                    created_at=repository.created_at,
                    updated_at=repository.updated_at,
                    pushed_at=repository.pushed_at,
                    # == Counts Properties
                    stargazers_count=repository.stargazers_count,
                    watchers_count=repository.subscribers_count,
                    forks_count=repository.forks_count,
                    open_issues_count=repository.open_issues_count,
                    # == Features Properties
                    has_issues=repository.has_issues,
                    has_discussions=repository._rawData["has_discussions"],
                    has_wiki=repository.has_wiki,
                    has_pages=repository.has_pages,
                    has_projects=repository.has_projects,
                    has_downloads=repository.has_downloads,
                    # == Type Properties
                    is_fork=repository.fork,
                    is_template=repository.is_template,
                    is_archived=repository.archived,
                )

                # Update the lowest known repository
                match order:
                    case "stars":
                        previous = min(previous, repository.stargazers_count)
                    case "forks":
                        previous = min(previous, repository.forks_count)

                # Update the progress bar
                pbar.update(len(repositories) - pbar.n)

                # Break if we are done
                if len(repositories) == amount:
                    break

    return list(repositories.values())
