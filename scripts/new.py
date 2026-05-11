import re
from os import makedirs
from string import Template

from click import command, option

FILE_MAPPINGS = {
    ".template/code/handler.pyt": "templates/{name}/handler.py",
    ".template/code/settings.pyt": "templates/{name}/settings.py",
    ".template/code/models.pyt": "templates/{name}/models.py",
    ".template/tests/test_handler.pyt": "tests/{name}/test_handler.py",
    ".template/stacks/template.pyt": "infra/stacks/{name}.py",
    ".template/docs/template.md": "docs/template/{name}.md",
    ".template/docs/reference.md": "docs/reference/{name}.md",
}


def update_infra_app_file(name: str, camel_name: str):
    """Update infra/app.py to include new template in STACK_REGISTRY."""
    with open("infra/app.py", "r") as f:
        content = f.read()

    import_line = f"from infra.stacks.{name} import {camel_name}Stack"
    if import_line not in content:
        # Find the last stack import
        lines = content.splitlines()
        last_import_idx = -1
        for i, line in enumerate(lines):
            if "from infra.stacks." in line:
                last_import_idx = i

        lines.insert(last_import_idx + 1, import_line)

        # Update STACK_REGISTRY
        content = "\n".join(lines)
        registry_match = re.search(r"STACK_REGISTRY: dict\[str, type\] = \{(.*?)\}", content, re.DOTALL)
        if registry_match:
            registry_content = registry_match.group(1)
            new_registry_entry = f'    "{name}": {camel_name}Stack,'
            if f'"{name}":' not in registry_content:
                updated_registry = registry_content.rstrip() + "\n" + new_registry_entry + "\n"
                content = content.replace(registry_content, updated_registry)
                content += "\n"  # Ensure file ends with a newline

        with open("infra/app.py", "w") as f:
            f.write(content)


def update_deploy_workflow(name: str):
    """Update .github/workflows/deploy.yml to include new template in options and matrix."""
    with open(".github/workflows/deploy.yml", "r") as f:
        content = f.read()

    if f"- {name}" not in content:
        # Update options
        options_match = re.search(r"options:\n(.*?)(?=\n\w+:|$)", content, re.DOTALL)
        if options_match:
            options_content = options_match.group(1)
            if f"- {name}" not in options_content:
                updated_options = options_content.rstrip() + f"\n          - {name}\n"
                content = content.replace(options_content, updated_options)

        # Update matrix
        matrix_match = re.search(r"matrix:\n\s+stack: \[(.*?)\]", content)
        if matrix_match:
            matrix_content = matrix_match.group(1)
            if name not in matrix_content:
                updated_matrix = matrix_content + f", {name}"
                content = content.replace(f"stack: [{matrix_content}]", f"stack: [{updated_matrix}]")

        with open(".github/workflows/deploy.yml", "w") as f:
            f.write(content)


def update_mkdocs_file(name: str, title_name: str):
    """Update mkdocs.yml to include new template in both Template and Reference sections."""
    with open("mkdocs.yml", "r") as f:
        content = f.read()

    if f"{name}.md" not in content:
        # Add to Templates
        templates_match = re.search(r"Templates:\n(.*?)(?=\n  - Reference:|$)", content, re.DOTALL)
        if templates_match:
            templates_content = templates_match.group(1)
            new_entry = f"    - {title_name}: template/{name}.md"
            if new_entry not in templates_content:
                updated_templates = templates_content.rstrip() + "\n" + new_entry
                content = content.replace(templates_content, updated_templates)

        # Add to Reference
        reference_match = re.search(r"Reference:\n(.*?)(?=\nplugins:|$)", content, re.DOTALL)
        if reference_match:
            reference_content = reference_match.group(1)
            new_entry = f"    - {title_name}: reference/{name}.md"
            if new_entry not in reference_content:
                updated_reference = reference_content.rstrip() + "\n" + new_entry + "\n"
                content = content.replace(reference_content, updated_reference)

        with open("mkdocs.yml", "w") as f:
            f.write(content)


def update_mise_toml(name: str):
    """Update mise.toml to include new template in deploy and destroy targets."""
    with open("mise.toml", "r") as f:
        content = f.read()

    if f"|{name}" not in content:
        # Update usage messages using regex
        content = re.sub(r"(Usage: mise run (?:deploy|destroy) stack=<[a-z0-9|]+)>", r"\1|" + name + ">", content)

        # Update case statements
        lines = content.splitlines()
        new_lines = []
        for line in lines:
            if '*) echo "Error: unknown stack' in line:
                components = name.split("_")
                camel_name = "".join(x.title() for x in components)
                new_lines.append(f"    {name}) CDK_STACK={camel_name}Stack ;;")
            new_lines.append(line)

        with open("mise.toml", "w") as f:
            f.write("\n".join(new_lines) + "\n")


@command(context_settings={"help_option_names": ["-h", "--help"]}, help="Generate new template")
@option("-n", "--name", help="Template name", required=True)
def main(name: str):

    # Read name and generate variants
    name = name.lower().replace("-", "_")
    components = name.split("_")
    camel_name = "".join(x.title() for x in components)
    title_name = " ".join(x.title() for x in components)

    # Create directories
    makedirs(f"templates/{name}", exist_ok=True)
    makedirs(f"tests/{name}", exist_ok=True)

    # Generate __init__.py files
    with open(f"templates/{name}/__init__.py", "w") as f:
        pass
    with open(f"tests/{name}/__init__.py", "w") as f:
        pass

    # Generate all other files from templates
    for template_file, target_file in FILE_MAPPINGS.items():
        with open(template_file, "r") as f:
            template = Template(f.read())
        with open(target_file.format(name=name), "w") as f:
            f.write(template.substitute(name=name, camel_name=camel_name, title_name=title_name))

    # Update Registry Files
    update_infra_app_file(name, camel_name)
    update_deploy_workflow(name)
    update_mkdocs_file(name, title_name)
    update_mise_toml(name)

    print(f"Successfully created template '{name}'")


if __name__ == "__main__":
    main()
