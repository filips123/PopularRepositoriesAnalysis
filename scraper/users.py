from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from github import Github
from tqdm import tqdm


@dataclass
class User:
    # == Basic Properties

    id: int
    """The internal account ID."""

    type: str
    """The account type (user or organization)."""

    username: str
    """The account username."""

    url: str
    """The account URL."""

    # == Social Properties

    name: str | None
    """The account name, if set."""

    homepage: str | None
    """The account homepage, if set."""

    email: str | None
    """The account email, if set."""

    company: str | None
    """The account company, if set."""

    location: str | None
    """The account location, if set."""

    hireable: bool
    """Whether the account is hireable."""

    # == Dates Properties

    created_at: datetime
    """The time the repository was created."""

    updated_at: datetime
    """The time the repository was last updated."""

    # == Counts Properties

    followers_count: int
    """The number of accounts that follow this account."""

    following_count: int
    """The number of accounts that this account follows."""

    public_repositories_count: int
    """The number of public repositories of this account."""

    public_gists_count: int
    """The number of public gists of this account."""


def get_top_users(
    github: Github,
    order: Literal["followers", "repositories"],
    start: int = 0,
    amount: int | None = None,
) -> list[User]:
    """Get the top users by the specified order."""

    users: list[User] = []

    # We need to rename the params correctly as they are not consistent
    query_param = "followers" if order == "followers" else "repos"
    order_param = "followers" if order == "followers" else "repositories"

    end = start + amount if amount else None
    query = github.search_users(f"{query_param}:>1", sort=order_param, order="desc")[start:end]

    for user in tqdm(query, total=amount or 1020):
        users.append(
            User(
                # Basic Properties
                id=user.id,
                type=user.type,
                username=user.login,
                url=user.html_url,
                # Social Properties
                name=user.name or None,
                homepage=user.blog or None,
                email=user.email or None,
                company=user.company or None,
                location=user.location or None,
                hireable=bool(user.hireable),
                # Dates Properties
                created_at=user.created_at,
                updated_at=user.updated_at,
                # Counts Properties
                followers_count=user.followers,
                following_count=user.following,
                public_repositories_count=user.public_repos,
                public_gists_count=user.public_gists,
            )
        )

    return users
