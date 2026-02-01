"""Main entry point for cmdkit CLI."""

import re
import subprocess
import sys
from typing import List, Optional

import typer
from jinja2 import Template
from rich.console import Console
from rich.table import Table

from cmdkit import __version__
from cmdkit.storage import load_config, save_config

# Rich console for styled output
console = Console()
err_console = Console(stderr=True)


def print_success(message: str) -> None:
    """Print a success message with checkmark."""
    console.print(f"[green]✔[/green] {message}")


def print_error(message: str) -> None:
    """Print an error message with X mark."""
    err_console.print(f"[red]✖[/red] {message}")


def print_info(message: str) -> None:
    """Print an info message."""
    console.print(f"[dim]→[/dim] {message}")


def print_header(message: str) -> None:
    """Print a section header."""
    console.print(f"\n[bold]{message}[/bold]")

app = typer.Typer(
    name="cmdkit",
    help="A CLI tool for managing commands.",
    add_completion=False,
)


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console.print(f"cmdkit version [cyan]{__version__}[/cyan]")
        raise typer.Exit()

def arnav(value: bool) -> None:
    """Just to test option parsing."""
    if value:
        console.print("Arnav option activated.")
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
    print_info("Initializing cmdkit project...")
    console.print("[dim](Not implemented yet)[/dim]")


@app.command()
def save(
    name: str = typer.Argument(..., help="Name of the workflow"),
    commands: List[str] = typer.Argument(..., help="Commands to save in the workflow"),
) -> None:
    """Save a named workflow with one or more commands."""
    # Validate at least one command
    if not commands:
        print_error("At least one command is required.")
        raise typer.Exit(1)
    
    # Load existing config
    config = load_config()
    
    # Check if workflow already exists
    if name in config["workflows"]:
        print_error(f"Workflow [bold]{name}[/bold] already exists.")
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
    print_success(f"Saved workflow [bold]{name}[/bold] with {len(commands)} command(s).")
    if placeholders:
        print_info(f"Detected placeholders: [cyan]{', '.join(sorted(placeholders))}[/cyan]")


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
            console.print(f"[dim]Enter value for[/dim] [cyan]{{{{{placeholder}}}}}[/cyan]: ", end="")
            values[placeholder] = input()
    
    return values


@app.command(
    context_settings={"allow_extra_args": True, "allow_interspersed_args": False}
)
def run(
    ctx: typer.Context,
    workflow_name: str = typer.Argument(..., help="Name of the workflow to run"),
    dry: bool = typer.Option(False, "--dry", "--dry-run", help="Preview commands without executing"),
    stop_on_fail: bool = typer.Option(False, "--stop-on-fail", "-f", help="Stop execution on first failure (chain with &&)"),
    stop_on_success: bool = typer.Option(False, "--stop-on-success", "-s", help="Stop execution on first success (chain with ||)"),
) -> None:
    """Run a saved workflow with placeholder substitution."""
    # Validate mutually exclusive options
    if stop_on_fail and stop_on_success:
        print_error("Cannot use --stop-on-fail and --stop-on-success together.")
        raise typer.Exit(1)
    
    # Load config
    config = load_config()
    
    # Check if workflow exists
    if workflow_name not in config["workflows"]:
        print_error(f"Workflow [bold]{workflow_name}[/bold] not found.")
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
        print_header(f"Dry run: {workflow_name}")
        if stop_on_fail:
            console.print(f"  [dim]Mode:[/dim] stop on first failure (&&)")
        elif stop_on_success:
            console.print(f"  [dim]Mode:[/dim] stop on first success (||)")
        else:
            console.print(f"  [dim]Mode:[/dim] run all commands")
        for i, cmd in enumerate(rendered, 1):
            console.print(f"  [dim][{i}][/dim] [cyan]{cmd}[/cyan]")
        raise typer.Exit(0)
    
    # Execute based on mode
    print_header(f"Running: {workflow_name}")
    
    if stop_on_fail:
        # Chain with && - run as single command
        chained = " && ".join(rendered)
        console.print(f"\n[dim]Chained (&&):[/dim] [bold]{chained}[/bold]")
        result = subprocess.run(chained, shell=True)
        if result.returncode != 0:
            print_error(f"Command failed with exit code {result.returncode}")
            raise typer.Exit(result.returncode)
        print_success("Done")
    elif stop_on_success:
        # Chain with || - run as single command
        chained = " || ".join(rendered)
        console.print(f"\n[dim]Chained (||):[/dim] [bold]{chained}[/bold]")
        result = subprocess.run(chained, shell=True)
        if result.returncode != 0:
            print_error(f"All commands failed with exit code {result.returncode}")
            raise typer.Exit(result.returncode)
        print_success("Done")
    else:
        # Default: run all commands regardless of success/failure
        failed = []
        for i, cmd in enumerate(rendered, 1):
            console.print(f"\n[dim][{i}/{len(rendered)}][/dim] [bold]{cmd}[/bold]")
            result = subprocess.run(cmd, shell=True)
            if result.returncode != 0:
                print_error(f"Failed with exit code {result.returncode}")
                failed.append((i, cmd, result.returncode))
            else:
                print_success("Done")
        
        console.print()
        if failed:
            print_error(f"Workflow completed with {len(failed)} failed command(s).")
            raise typer.Exit(1)
    
    console.print()
    print_success(f"Workflow [bold]{workflow_name}[/bold] completed successfully.")


@app.command("list")
def list_workflows(
    tag_filter: Optional[str] = typer.Option(None, "--tag", "-t", help="Filter workflows by tag"),
) -> None:
    """List all saved workflows."""
    config = load_config()
    workflows = config["workflows"]
    
    if not workflows:
        print_info("No workflows saved yet.")
        raise typer.Exit(0)
    
    # Filter by tag if specified
    if tag_filter:
        filtered = {
            name: wf for name, wf in workflows.items()
            if tag_filter in wf.get("tags", [])
        }
        if not filtered:
            print_info(f"No workflows found with tag [cyan]{tag_filter}[/cyan].")
            raise typer.Exit(0)
        workflows = filtered
    
    # Create table
    table = Table(show_header=True, header_style="bold")
    table.add_column("Name")
    table.add_column("Tags")
    
    for name, wf in sorted(workflows.items()):
        tags = wf.get("tags", [])
        tag_str = ", ".join(tags) if tags else "[dim]-[/dim]"
        table.add_row(name, tag_str)
    
    console.print(table)


@app.command()
def tag(
    workflow_name: str = typer.Argument(..., help="Name of the workflow to tag"),
    tag_name: str = typer.Argument(..., help="Tag to add to the workflow"),
) -> None:
    """Add a tag to a workflow."""
    config = load_config()
    
    # Check if workflow exists
    if workflow_name not in config["workflows"]:
        print_error(f"Workflow [bold]{workflow_name}[/bold] not found.")
        raise typer.Exit(1)
    
    workflow = config["workflows"][workflow_name]
    tags = workflow.get("tags", [])
    
    # Add tag if not already present
    if tag_name in tags:
        print_info(f"Workflow [bold]{workflow_name}[/bold] already has tag [cyan]{tag_name}[/cyan].")
    else:
        tags.append(tag_name)
        workflow["tags"] = tags
        save_config(config)
        print_success(f"Added tag [cyan]{tag_name}[/cyan] to workflow [bold]{workflow_name}[/bold].")


@app.command()
def search(
    query: str = typer.Argument(..., help="Search term to find workflows"),
) -> None:
    """Search for workflows by name, tags, or commands."""
    config = load_config()
    workflows = config["workflows"]
    
    if not workflows:
        print_info("No workflows saved yet.")
        raise typer.Exit(0)
    
    query_lower = query.lower()
    matches = []
    
    for name, wf in workflows.items():
        score = 0
        
        # Exact match on name
        if query_lower == name.lower():
            score = 100
        # Name contains query
        elif query_lower in name.lower():
            score = 80
        # Query contains part of name
        elif any(part in query_lower for part in name.lower().split("-")):
            score = 60
        # Match in tags
        elif any(query_lower in tag.lower() for tag in wf.get("tags", [])):
            score = 50
        # Match in commands
        elif any(query_lower in cmd.lower() for cmd in wf.get("commands", [])):
            score = 30
        
        if score > 0:
            matches.append((name, wf, score))
    
    if not matches:
        print_info(f"No workflows found matching [cyan]{query}[/cyan].")
        raise typer.Exit(0)
    
    # Sort by score (highest first)
    matches.sort(key=lambda x: (-x[2], x[0]))
    
    console.print(f"Found [bold]{len(matches)}[/bold] workflow(s) matching [cyan]{query}[/cyan]:\n")
    
    # Create table
    table = Table(show_header=True, header_style="bold")
    table.add_column("Name")
    table.add_column("Tags")
    
    for name, wf, score in matches:
        tags = wf.get("tags", [])
        tag_str = ", ".join(tags) if tags else "[dim]-[/dim]"
        table.add_row(name, tag_str)
    
    console.print(table)


if __name__ == "__main__":
    app()
