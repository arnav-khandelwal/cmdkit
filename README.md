# cmdkit

![Version](https://img.shields.io/badge/version-0.1.3-blue)

A lightweight CLI tool for saving, organizing, and running reusable shell command workflows.

Save complex multi-step commands once, run them anywhere with placeholder substitution.

## Installation

### macOS / Linux
```sh
curl -fsSL https://raw.githubusercontent.com/arnav-khandelwal/cmdkit/main/install.sh | sh
```
### Windows
```sh
iwr https://raw.githubusercontent.com/arnav-khandelwal/cmdkit/main/install.ps1 -useb | iex
```

## Features

- **Save workflows** – Store named sequences of shell commands
- **Placeholders** – Use `{{variable}}` syntax for dynamic values
- **Run modes** – Execute all commands, stop on failure, or stop on success
- **Dry run** – Preview commands before executing
- **Tags** – Organize workflows with custom tags
- **Search** – Find workflows by name, tags, or command content
- **Rich output** – Clean, readable terminal output with tables and colors

## Status
cmdkit is in early development (v0.1.3).
Core workflow creation and execution are stable.
Editing and advanced management features are planned.

## Quick Start

```bash
# Save a workflow
cmdkit save deploy "git pull" "npm install" "npm run build" "pm2 restart app"

# Run it
cmdkit run deploy

# Save a workflow with placeholders
cmdkit save git-commit "git add ." "git commit -m {{message}}" "git push"

# Run with placeholder values
cmdkit run git-commit --message "fix: resolve login bug"

# List all workflows
cmdkit list

# Search workflows
cmdkit search git
```

## Commands

### `cmdkit save <name> <commands...>`

Save a new workflow with one or more commands.

```bash
cmdkit save morning-routine "echo Good morning!" "date" "cal"
cmdkit save backup "tar -czf backup.tar.gz ./data" "aws s3 cp backup.tar.gz s3://bucket/"
```

Placeholders are automatically detected:

```bash
cmdkit save greet "echo Hello, {{name}}!"
# Output: ✔ Saved workflow greet with 1 command(s).
#         → Detected placeholders: name
```

### `cmdkit run <workflow> [OPTIONS] [--placeholder value...]`

Run a saved workflow.

```bash
cmdkit run morning-routine
cmdkit run greet --name "World"
```

**Options:**

| Option | Short | Description |
|--------|-------|-------------|
| `--dry` / `--dry-run` | | Preview commands without executing |
| `--stop-on-fail` | `-f` | Stop at first failure (chains with `&&`) |
| `--stop-on-success` | `-s` | Stop at first success (chains with `\|\|`) |

**Run modes:**

```bash
# Default: run all commands, report failures at end
cmdkit run deploy

# Stop on first failure (like cmd1 && cmd2 && cmd3)
cmdkit run --stop-on-fail deploy

# Stop on first success (like cmd1 || cmd2 || cmd3)
cmdkit run --stop-on-success deploy

# Preview without executing
cmdkit run --dry deploy
```

**Placeholder prompting:**

If a placeholder value is not provided via CLI, you'll be prompted:

```bash
$ cmdkit run greet
Enter value for {{name}}: Alice
```

### `cmdkit list [OPTIONS]`

List all saved workflows in a table.

```bash
cmdkit list
```

Output:
```
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Name         ┃ Tags       ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ deploy       │ -          │
│ git-commit   │ git, daily │
│ greet        │ -          │
└──────────────┴────────────┘
```

**Filter by tag:**

```bash
cmdkit list --tag git
cmdkit list -t daily
```

### `cmdkit tag <workflow> <tag>`

Add a tag to a workflow for organization.

```bash
cmdkit tag git-commit git
cmdkit tag git-commit daily
```

### `cmdkit search <query>`

Search workflows by name, tags, or command content.

```bash
cmdkit search git      # Matches workflow names and tags
cmdkit search deploy   # Matches workflow names
cmdkit search npm      # Matches command content
```

Results are ranked by relevance (exact name > partial name > tags > commands).

## Data Storage

Workflows are stored in `~/.cmdkit/config.json`:

```json
{
  "workflows": {
    "git-commit": {
      "commands": [
        "git add .",
        "git commit -m {{message}}",
        "git push"
      ],
      "tags": ["git", "daily"]
    }
  }
}
```

## Examples

### Git workflow

```bash
cmdkit save git-everyday "git add ." "git commit -m {{msg}}" "git push"
cmdkit tag git-everyday git
cmdkit run git-everyday --msg "feat: add user authentication"
```

### Docker deployment

```bash
cmdkit save docker-deploy \
  "docker build -t {{image}}:{{tag}} ." \
  "docker push {{image}}:{{tag}}" \
  "kubectl set image deployment/{{app}} {{app}}={{image}}:{{tag}}"

cmdkit run docker-deploy --image myapp --tag v1.2.3 --app myservice
```

### Testing with fallback

```bash
cmdkit save test-suite "npm test" "npm run test:e2e" "npm run test:integration"

# Run all tests regardless of failures
cmdkit run test-suite

# Stop at first failure
cmdkit run --stop-on-fail test-suite
```

### Health checks

```bash
cmdkit save health-check \
  "curl -f http://service1/health" \
  "curl -f http://service2/health" \
  "curl -f http://service3/health"

# Stop at first success (any healthy service)
cmdkit run --stop-on-success health-check
```

## Requirements

- Python 3.10+
- Dependencies: Typer, Jinja2, Rich


## License

This project is licensed under the MIT License.
