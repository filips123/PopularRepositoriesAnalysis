from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from github import Github
from tqdm import tqdm


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


def get_top_repositories(
    github: Github,
    order: Literal["stars", "forks"],
    start: int = 0,
    amount: int | None = None,
) -> list[Repository]:
    """Get the top repositories by the specified order."""

    repositories: list[Repository] = []

    end = start + amount if amount else None
    query = github.search_repositories(f"{order}:>1", sort=order, order="desc")[start:end]

    for repository in tqdm(query, total=amount or 1020):
        repositories.append(
            Repository(
                # Basic Properties
                id=repository.id,
                owner=repository.owner.login,
                name=repository.name,
                url=repository.html_url,
                size=repository.size,
                default_branch=repository.default_branch,
                license=repository.license.spdx_id if repository.license else None,
                language=repository.language or None,
                languages=repository.get_languages(),
                # Social Properties
                description=repository.description or None,
                homepage=repository.homepage or None,
                topics=repository.topics,
                # Dates Properties
                created_at=repository.created_at,
                updated_at=repository.updated_at,
                pushed_at=repository.pushed_at,
                # Counts Properties
                stargazers_count=repository.stargazers_count,
                watchers_count=repository.subscribers_count,
                forks_count=repository.forks_count,
                open_issues_count=repository.open_issues_count,
                # Features Properties
                has_issues=repository.has_issues,
                has_discussions=repository._rawData["has_discussions"],
                has_wiki=repository.has_wiki,
                has_pages=repository.has_pages,
                has_projects=repository.has_projects,
                has_downloads=repository.has_downloads,
                # Type Properties
                is_fork=repository.fork,
                is_template=repository.is_template,
                is_archived=repository.archived,
            )
        )

    return repositories
