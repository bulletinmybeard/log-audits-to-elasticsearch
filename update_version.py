import re
import subprocess
import sys
from contextlib import contextmanager
from typing import Generator, List

import toml

from service_audit.custom_logger import get_logger

logger = get_logger("audit_service")


def poetry_lock_no_update() -> None:
    try:
        result = subprocess.run(
            ["poetry", "lock", "--no-update"],
            check=True,
            capture_output=True,
            text=True,
        )
        logger.info("Poetry lock updated. %s", result.stdout)
    except subprocess.CalledProcessError as e:
        logger.error("Error running poetry lock: %s %s", e, e.stderr)


def get_current_version() -> str:
    file_path = "pyproject.toml"
    try:
        pyproject_data = toml.load(file_path)
        current_version = pyproject_data["tool"]["poetry"]["version"]
        return current_version
    except FileNotFoundError:
        logger.error("%s not found", file_path)
        sys.exit(1)
    except KeyError as e:
        logger.error(f"Error loading %s: %s", file_path, e)
        sys.exit(1)


if len(sys.argv) != 2:
    logger.warning("Usage: python update_version.py <new_version>")
    sys.exit(1)

arg_current_version = get_current_version()
arg_new_version = str(sys.argv[1])

semver_regex = r"^\d+\.\d+\.\d+$"

# Check if both versions match the Semantic Versioning pattern.
if not re.match(semver_regex, arg_current_version):
    logger.error(
        f"Error: Current version '{arg_current_version}' "
        f"does not match the Semantic Versioning pattern."
    )
    sys.exit(1)

if not re.match(semver_regex, arg_new_version):
    logger.error(
        f"Error: New version '{arg_new_version}' "
        f"does not match the Semantic Versioning pattern."
    )
    sys.exit(1)

# Abort if both versions are identical.
if arg_current_version == arg_new_version:
    logger.error(
        f"Error: New version '{arg_new_version}' is the same as the current version "
        f"'{arg_current_version}' (nothing to do here...bye!)."
    )
    sys.exit(1)

# File paths where the version numbers should be updated.
file_path_list = [
    "service_audit/__init__.py",
    "service_audit/main.py",
]

error_messages = []


@contextmanager
def update_version_in_file(
    file_path: str, current_version: str, new_version: str
) -> Generator[None, None, None]:
    # Read the file.
    with open(file_path, "r") as file:
        content = file.read()

    version_pattern = re.compile(
        r'(__version__\s*=\s*|version\s*=\s*)["\']'
        + re.escape(current_version)
        + "[\"']"
    )

    # Check if the current version is in the file.
    if not version_pattern.search(content):
        error_messages.append(
            f"Error: current version '{current_version}' not found in '{file_path}'"
        )
        yield
        return

    try:
        # Write the updated content back to the file.
        with open(file_path, "w") as file:
            # Replace the current version with the new version.
            file.write(version_pattern.sub(r'\g<1>"' + new_version + '"', content))
    except Exception as e:
        error_messages.append(f"Error: {e}")
        yield
        return

    logger.info("Updated version in %s to %s", file_path, file_path, new_version)
    yield


def update_versions(
    file_paths: List[str], current_version: str, new_version: str
) -> None:
    for file_path in file_paths:
        with update_version_in_file(file_path, current_version, new_version):
            pass

    if error_messages:
        for error in error_messages:
            logger.error(error)
        sys.exit(1)
    else:
        poetry_lock_no_update()


# Update the versions.
update_versions(file_path_list, arg_current_version, arg_new_version)
