import sys

arguments = sys.argv[1:]

# easier to do this than to use some cli framework
match arguments:
    case ["scrape", *targets]:
        from .scraper import scrape, spiders

        if not all(target in spiders for target in targets):
            print(f"Targets must be members of {spiders}")
            print("Usage: python -m oleorcarl {scrape, dev, build} [*targets]")
            sys.exit()

        scrape(targets=targets)

    case ["dev"]:
        from . import app

        app.run(debug=True, port=3000, host="localhost")

    case ["build"]:
        from .freezer import freeze

        freeze()

    case ["test"]:
        from .freezer import test

        test()

    case _:
        print(f"Invalid arguments: {arguments}.")
        print("Usage: python -m oleorcarl {scrape, dev, build} [*targets]")
        sys.exit()
