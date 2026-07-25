Pull requests are very welcome although for sizable tasks it may be worth
discussing via a GitHub issue before undertaking too much work.

## Development

The project uses [uv](https://docs.astral.sh/uv/):

    uv sync                       # create the environment
    uv run pytest --cov           # tests + conformance (coverage must stay 100%)
    uv run ruff check pyuca scripts tests
    uv run ruff format --check pyuca scripts tests
    uv run pyright

All of the above must pass. Because `sort_key` normalizes with the standard
library's `unicodedata`, the conformance suite for a given UCA version only runs
on an interpreter whose Unicode version matches; CI covers 3.11–3.14 so that
14.0.0–16.0.0 are each exercised on their matching runtime.

The bundled DUCET tables and conformance fixtures are downloaded from
unicode.org and can be regenerated with:

    python scripts/fetch_ducet.py

If you have any problems, questions or suggestions, please file an issue on
GitHub.
