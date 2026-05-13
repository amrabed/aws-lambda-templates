from aws_cdk.aws_lambda import Code


def get_lambda_code() -> Code:
    """Returns a standardized Code object that excludes unnecessary local files."""
    return Code.from_asset(
        path=".",
        exclude=[
            ".git",
            ".github",
            ".venv",
            ".vscode",
            "pyproject.toml",
            "mise.toml",
            "mkdocs.yml",
            "docs",
            "tests",
            "infra",
            "cdk.json",
            "cdk.out",
            "__pycache__",
            ".pytest_cache",
            ".ruff_cache",
            ".hypothesis",
        ],
    )
