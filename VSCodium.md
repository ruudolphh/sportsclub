# Python on VSCodium

This project has been created using [VSCodium](https://vscodium.com/) with the `Python` extension by Microsoft and the `Ruff` extension by Charlie R. Marsh. These are the steps followed to install and configure the environment.

## Install the extension

Start by installing the extensions:

1. Open VSCodium.
2. Open the `Extensions` tab via `Ctrl + Shift + X`.
3. Search for `Python` by `ms-python` and install it.
4. Search for `Ruff` by `charliermarsh` and install it.

## Configure the extension

Continue by configuring the VS Codium settings via the `.vscode/settings.json` file:

```json
{
    // Python interpreter
    "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
    
    // Ruff extension settings
    "ruff.nativeServer": "on",
    "ruff.interpreter": ["${workspaceFolder}/.venv/bin/python"],
    
    // Python-specific editor settings
    "[python]": {
        "editor.formatOnSave": true,
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.codeActionsOnSave": {
            "source.fixAll": "explicit",
            "source.organizeImports": "explicit"
        }
    },
    
    // Disable other Python linters to avoid conflicts
    "python.linting.enabled": false,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": false
}
```

## Create a project configuration file

Create a file named `pyproject.toml` with the following content:

```ini
[tool.ruff]
line-length = 88
target-version = "py312"

[tool.ruff.lint]
# Enable many rules for better code quality
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes (includes F401 for unused imports)
    "I",    # isort (import sorting)
    "N",    # pep8-naming
    "UP",   # pyupgrade
    "B",    # flake8-bugbear (common bugs)
    "C4",   # flake8-comprehensions
    "SIM",  # flake8-simplify
]

# You can ignore specific rules if needed
ignore = []

[tool.ruff.lint.isort]
known-first-party = ["sportsclub"]
```

## Restart the Ruff server

Finally, we just need to restart the Ruff server:

1. Open the `Command Palette` via `Ctrl+Shift+P`.
2. Type `Ruff` and select the `Ruff: Restart Server` option.
