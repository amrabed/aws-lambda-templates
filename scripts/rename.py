import os
import re
import shutil
from pathlib import Path

from click import ClickException, UsageError, command, echo, option


@command()
@option("--name", required=True, help="Project new name")
@option("--description", required=True, help="Project short description")
@option("--author", required=True, help="Author name")
@option("--email", required=True, help="Author email")
@option("--github", required=True, help="GitHub username")
def main(name: str, description: str, author: str, email: str, github: str):
    # Validate name to prevent directory traversal or other injection
    if not re.match(r"^[a-zA-Z0-9_-]+$", name):
        raise UsageError(
            f"Invalid project name '{name}'. Only alphanumeric characters, dashes, and underscores are allowed."
        )

    source = name.replace("-", "_").lower()

    echo(f"Initializing project '{name}' (source: '{source}')...")

    # 1. Rename templates directory
    if os.path.isdir("templates"):
        shutil.move("templates", source)
    elif not os.path.isdir(source):
        raise ClickException(f"Error: Neither 'templates' nor '{source}' directory found.")

    # 2. File modifications
    replacements = [
        ("mkdocs.yml", r"^repo_name: .*", f"repo_name: {github}/{name}"),
        ("mkdocs.yml", r"^repo_url: .*", f"repo_url: https://github.com/{github}/{name}"),
        ("pyproject.toml", r'^name = ".*"', f'name = "{name}"'),
        ("pyproject.toml", r'^description = ".*"', f'description = "{description}"'),
        ("pyproject.toml", r"^authors = \[.*\]", f'authors = [{{name = "{author}", email = "{email}"}}]'),
        ("pyproject.toml", r'^source = \["templates"\]', f'source = ["{source}"]'),
        ("mise.toml", r'default="templates"', f'default="{name}"'),
        ("mise.toml", r'default="AWS Lambda Templates"', f'default="{description}"'),
        ("mise.toml", r'default="Amr Abed"', f'default="{author}"'),
        ("mise.toml", r'default="amrabed"', f'default="{github}"'),
        ("docs/README.md", r"^# .*", f"# {description}"),
        (".github/CODEOWNERS", r"@.*", f"@{github}"),
        (".github/FUNDING.yml", r"^github: .*", f"github: {github}"),
    ]

    for filepath, pattern, replacement in replacements:
        path = Path(filepath)
        if not path.exists():
            echo(f"Warning: File {filepath} not found, skipping.")
            continue

        content = path.read_text()
        new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        path.write_text(new_content)
        echo(f"Updated {filepath}")

    # 3. Global search and replace for 'templates'
    echo(f"Replacing 'templates.' and 'templates/' with '{source}.' and '{source}/'...")
    for root, dirs, files in os.walk("."):
        # Skip .git, .venv, and other hidden directories
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "venv"]

        for file in files:
            if file.endswith((".py", ".md", ".yml", ".pyt", ".toml")):
                path = Path(root) / file
                if path.name == "rename.py":
                    continue

                content = path.read_text()
                # Replace 'templates.' (imports), 'templates/' (paths), and '"templates"' (config strings)
                new_content = content.replace("templates.", f"{source}.")
                new_content = new_content.replace("templates/", f"{source}/")
                new_content = new_content.replace('"templates"', f'"{source}"')

                if new_content != content:
                    path.write_text(new_content)
                    echo(f"Updated references in {path}")

    echo("Project initialization complete.")


if __name__ == "__main__":
    main()
