import sys

arguments = sys.argv[1:]

match arguments:
    case ["scrape", *targets]:
        from .scraper import scrape, spiders
        if not all(target in spiders for target in targets):
            print(f"Targets must be members of {spiders}")
            sys.exit()

        scrape(targets=targets)

    case ["dev"]:
        from .app import app
        app.run(debug=True)

    case ["build"]:
        raise NotImplementedError

    case _:
        print("Invalid arguments '{}'.")
        print("Usage: {scrape, dev, build} [*targets]")
        sys.exit()


# TODO add CLI

# init
# - ask for confirmation
# - create new database

# scrape (args: --stolaf --carleton --all)
# - launch scraper

# dev
# - run flask dev server
# - run tailwind with --watch (subprocess, pipe output to stdout?)

# start/run?
# - build css w/ tailwind
# - run flask production server
