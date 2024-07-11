from pathlib import Path

import orjson
from github import Auth, Github

from repositories import get_top_repositories


def main() -> None:
    root = Path(__file__).parents[1]

    with root.joinpath("scraper").joinpath("auth.txt").open(encoding="utf-8") as file:
        token = file.read().strip()
        auth = Auth.Token(token)

    github = Github(auth=auth)
    # enable_console_debug_logging()

    repositories = get_top_repositories(github)

    with root.joinpath("data").joinpath("repositories.json").open("wb") as file:
        serialized = orjson.dumps(repositories)
        file.write(serialized)
        file.write(b"\n")


if __name__ == "__main__":
    main()
