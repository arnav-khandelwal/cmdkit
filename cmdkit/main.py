"""Main entry point for cmdkit CLI."""

import re
import subprocess
import sys
from typing import List, Optional

import typer
from jinja2 import Template

from cmdkit import __version__
from cmdkit.storage import load_config, save_config

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

def arnav(value: bool) -> None:
    """Just to test option parsing."""
    if value:
        print("Arnav option activated.")
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
    arnav: bool = typer.Option(
        False,
        "--arnav", help="Just to test option parsing.",
        callback=arnav,
        is_eager=True,
    )
) -> None:
    """cmdkit - A CLI tool for managing commands."""
    pass


@app.command()
def init() -> None:
    """Initialize a new cmdkit project."""
    print("Initializing cmdkit project...")
    print("(Not implemented yet)")


@app.command()
def save(
    name: str = typer.Argument(..., help="Name of the workflow"),
    commands: List[str] = typer.Argument(..., help="Commands to save in the workflow"),
) -> None:
    """Save a named workflow with one or more commands."""
    # Validate at least one command
    if not commands:
        print("Error: At least one command is required.")
        raise typer.Exit(1)
    
    # Load existing config
    config = load_config()
    
    # Check if workflow already exists
    if name in config["workflows"]:
        print(f"Error: Workflow '{name}' already exists.")
        raise typer.Exit(1)
    
    # Detect placeholders using {{variable}} pattern
    placeholder_pattern = re.compile(r"\{\{(\w+)\}\}")
    placeholders = set()
    for cmd in commands:
        matches = placeholder_pattern.findall(cmd)
        placeholders.update(matches)
    
    # Save workflow
    config["workflows"][name] = {
        "commands": list(commands),
        "tags": [],
    }
    save_config(config)
    
    # Print success message
    print(f"Saved workflow '{name}' with {len(commands)} command(s).")
    if placeholders:
        print(f"Detected placeholders: {', '.join(sorted(placeholders))}")


def extract_placeholders(commands: List[str]) -> set:
    """Extract unique placeholder names from commands."""
    pattern = re.compile(r"\{\{(\w+)\}\}")
    placeholders = set()
    for cmd in commands:
        matches = pattern.findall(cmd)
        placeholders.update(matches)
    return placeholders


def render_commands(commands: List[str], values: dict) -> List[str]:
    """Render commands by replacing placeholders with values using Jinja2."""
    rendered = []
    for cmd in commands:
        # Convert {{var}} to Jinja2 {{ var }} syntax
        jinja_cmd = re.sub(r"\{\{(\w+)\}\}", r"{{ \1 }}", cmd)
        template = Template(jinja_cmd)
        rendered.append(template.render(**values))
    return rendered


def collect_placeholder_values(
    placeholders: set,
    cli_args: List[str],
) -> dict:
    """Collect placeholder values from CLI args or prompt user."""
    values = {}
    
    # Parse CLI args (--name value format)
    i = 0
    while i < len(cli_args):
        arg = cli_args[i]
        if arg.startswith("--"):
            key = arg[2:]
            if i + 1 < len(cli_args) and not cli_args[i + 1].startswith("--"):
                values[key] = cli_args[i + 1]
                i += 2
            else:
                i += 1
        else:
            i += 1
    
    # Prompt for missing placeholders
    for placeholder in sorted(placeholders):
        if placeholder not in values:
            values[placeholder] = input(f"Enter value for {{{{{placeholder}}}}}: ")
    
    return values


@app.command(
    context_settings={"allow_extra_args": True, "allow_interspersed_args": False}
)
def run(
    ctx: typer.Context,
    workflow_name: str = typer.Argument(..., help="Name of the workflow to run"),
    dry: bool = typer.Option(False, "--dry", "--dry-run", help="Preview commands without executing"),
) -> None:
    """Run a saved workflow with placeholder substitution."""
    # Load config
    config = load_config()
    
    # Check if workflow exists
    if workflow_name not in config["workflows"]:
        print(f"Error: Workflow '{workflow_name}' not found.")
        raise typer.Exit(1)
    
    workflow = config["workflows"][workflow_name]
    commands = workflow["commands"]
    
    # Extract placeholders
    placeholders = extract_placeholders(commands)
    
    # Collect values from CLI args or prompt
    values = collect_placeholder_values(placeholders, ctx.args)
    
    # Render commands
    rendered = render_commands(commands, values)
    
    # Dry-run mode: just print and exit
    if dry:
        print(f"Dry run for workflow '{workflow_name}':")
        for i, cmd in enumerate(rendered, 1):
            print(f"  [{i}] {cmd}")
        raise typer.Exit(0)
    
    # Execute commands sequentially
    print(f"Running workflow '{workflow_name}'...")
    for i, cmd in enumerate(rendered, 1):
        print(f"\n[{i}/{len(rendered)}] {cmd}")
        result = subprocess.run(cmd, shell=True)
        if result.returncode != 0:
            print(f"\nError: Command failed with exit code {result.returncode}")
            raise typer.Exit(result.returncode)
    
    print(f"\nWorkflow '{workflow_name}' completed successfully.")


if __name__ == "__main__":
    app()
