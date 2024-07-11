import argparse
from pathlib import Path

import orjson
from github import Auth, Github, enable_console_debug_logging

from repositories import get_top_repositories
from users import get_top_users


def main() -> None:
    # == Prepare the argument parser

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    parser.add_argument("--debug", action="store_true", help="enable request debugging")
    parser.add_argument("--start", type=int, default=0, help="the initial result offset")
    parser.add_argument("--amount", type=int, default=None, help="the amount of results")

    parser_repositories = subparsers.add_parser("repositories", help="scrape the top repositories")
    parser_repositories.add_argument("order", choices=("stars", "forks"))

    parser_users = subparsers.add_parser("users", help="scrape the top users")
    parser_users.add_argument("order", choices=("followers", "repositories"))

    args = parser.parse_args()

    # == Prepare the API client

    root = Path(__file__).parents[1]

    with root.joinpath("scraper").joinpath("auth.txt").open(encoding="utf-8") as file:
        token = file.read().strip()
        auth = Auth.Token(token)

    github = Github(auth=auth)

    if args.debug:
        enable_console_debug_logging()

    # == Run the correct scraper to collect the data

    data: list

    match args.command:
        case "repositories":
            data = get_top_repositories(github, args.order, args.start, args.amount)
        case "users":
            data = get_top_users(github, args.order, args.start, args.amount)
        case _:
            # This should not normally happen
            raise KeyError("Unknown command")

    # == Store the data to the correct file

    output = root.joinpath("data").joinpath(f"{args.command}-by-{args.order}.json")
    output.parent.mkdir(exist_ok=True, parents=True)

    with output.open("wb") as file:
        serialized = orjson.dumps(data)
        file.write(serialized)
        file.write(b"\n")


if __name__ == "__main__":
    main()
