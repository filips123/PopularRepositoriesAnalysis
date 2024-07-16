from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from github import Github
from tqdm import tqdm

CHUNK_MARGIN = 50
CHUNK_SIZE = float("inf")

QueryParam = Literal["followers", "repos"]
OrderParam = Literal["followers", "repositories"]


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


def find_max_value(
    github: Github,
    query_param: QueryParam,
    order_param: OrderParam,
) -> int:
    """Find the maximum number of followers/repositories any user has."""

    # We start the query from 1000 to make it slightly faster
    query = github.search_users(query=f"{query_param}:>1000", sort=order_param, order="desc")

    match order_param:
        case "followers":
            return int(query[0].followers)
        case "repositories":
            return int(query[0].get_repos().totalCount)


def get_top_users(
    github: Github,
    order: Literal["followers", "repositories"],
    amount: int,
) -> list[User]:
    """Get the top users by the specified order."""

    # We need to rename the params correctly as they are not consistent
    query_param: QueryParam = "followers" if order == "followers" else "repos"
    order_param: OrderParam = "followers" if order == "followers" else "repositories"

    # The maximum number of stars/forks any user has
    previous = find_max_value(github, query_param, order_param)

    users: dict[int, User] = {}

    with tqdm(total=amount) as pbar:
        # The search API limits the maximum number of results to 1000
        # To get more results, we need to query the API in smaller chunks

        while len(users) < amount:
            # We increase this slightly to account for possible increases
            chunk_max = previous + CHUNK_MARGIN
            chunk_min = max(chunk_max - CHUNK_SIZE, 1)

            # Set the progress bar description
            pbar.set_description(f"Chunk {chunk_min}-{chunk_max}")

            # Query all users in the chunk range
            query = github.search_users(
                f"{query_param}:{chunk_min}..{chunk_max}",
                sort=order_param,
                order="desc",
            )

            for user in query:
                # Add the user to the result
                users[user.id] = User(
                    # == Basic Properties
                    id=user.id,
                    type=user.type,
                    username=user.login,
                    url=user.html_url,
                    # == Social Properties
                    name=user.name or None,
                    homepage=user.blog or None,
                    email=user.email or None,
                    company=user.company or None,
                    location=user.location or None,
                    hireable=bool(user.hireable),
                    # == Dates Properties
                    created_at=user.created_at,
                    updated_at=user.updated_at,
                    # == Counts Properties
                    followers_count=user.followers,
                    following_count=user.following,
                    public_repositories_count=user.get_repos().totalCount,
                    public_gists_count=user.public_gists,
                )

                # Update the lowest known user
                match order:
                    case "followers":
                        previous = min(previous, user.followers)
                    case "repositories":
                        previous = min(previous, user.get_repos().totalCount)

                # Update the progress bar
                pbar.update(len(users) - pbar.n)

                # Break if we are done
                if len(users) == amount:
                    break

    return list(users.values())
