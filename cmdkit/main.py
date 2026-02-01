"""Main entry point for cmdkit CLI."""

import typer

from cmdkit import __version__

app = typer.Typer(
    name="cmdkit",
    help="A CLI tool for managing commands.",
    add_completion=False,
)


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        print(f"cmdkit version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """cmdkit - A CLI tool for managing commands."""
    pass


@app.command()
def init() -> None:
    """Initialize a new cmdkit project."""
    print("Initializing cmdkit project...")
    print("(Not implemented yet)")


if __name__ == "__main__":
    app()
