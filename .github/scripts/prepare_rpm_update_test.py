"""Prepare two RPM test versions without changing the production update source."""

import os
from pathlib import Path
import re


def prepare(root: Path, repository: str, run_id: str, attempt: str) -> dict[str, str]:
    if repository != "fluoz/bacakomik-app-flutter":
        raise ValueError("RPM test releases must stay in the test fork")
    if not run_id.isdecimal() or not attempt.isdecimal():
        raise ValueError("Run identifiers must be numeric")
    version = re.search(
        r"^version: (\d+)\.(\d+)\.(\d+)(?:\+\d+)?$",
        (root / "pubspec.yaml").read_text(),
        re.MULTILINE,
    )
    if version is None:
        raise ValueError("Expected a major.minor.patch+build pubspec version")
    major, minor, patch = map(int, version.groups())
    start = f"{major}.{minor}.{patch + 1}"
    update = f"{major}.{minor}.{patch + 2}"
    suffix = f"rpm-update-test-{run_id}-{attempt}"
    start_tag, update_tag = f"{start}-{suffix}", f"{update}-{suffix}"
    api = f"https://api.github.com/repos/{repository}/releases/tags/{update_tag}"
    variables = root / "lib/core/constants/variables.dart"
    source, count = re.subn(
        r"static const String latestReleaseApi\s*=\s*'[^']*';",
        f"static const String latestReleaseApi =\n      '{api}';",
        variables.read_text(),
    )
    if count != 1:
        raise ValueError("Expected exactly one latestReleaseApi constant")
    variables.write_text(source)

    start_url = f"https://github.com/{repository}/releases/tag/{start_tag}"
    update_url = f"https://github.com/{repository}/releases/tag/{update_tag}"
    notes = root / ".rpm-update-test"
    notes.mkdir(exist_ok=True)
    instructions = f"""## Fedora 45 in-app RPM update test

1. Download the **starter** RPM from {start_url}.
2. Install it: `sudo dnf install ./Yoru-{start}-linux-x86_64.rpm`.
3. Launch `/usr/bin/yoru` from a terminal to capture update diagnostics.
4. In More, select **Check for updates**, then **Update**.
5. First cancel the administrator prompt. Confirm the app stays open and
   `rpm -q yoru` still reports version {start}.
6. Retry, approve the administrator prompt, and wait for DNF to finish.
7. Confirm the app restarts, More shows {update}, and `rpm -q yoru` reports {update}.
8. Check for updates again: it should report that the app is up to date.

The update target is {update_url}. Install the starter first; let the app install
the target. Both test builds use that exact prerelease endpoint, so they do not
depend on GitHub's latest-release selection or affect the production updater.

If an earlier test already installed {update}, reset to the starter before repeating:

```sh
sudo dnf downgrade ./Yoru-{start}-linux-x86_64.rpm
```
After testing, install the desired production RPM; use `dnf downgrade` if its
version is lower. These packages use the regular Yoru installation and data.
"""
    (notes / "summary.md").write_text(instructions)
    (notes / "starter.md").write_text(
        "Install this RPM first to test the in-app update.\n\n" + instructions
    )
    (notes / "update.md").write_text(
        "Update target for the RPM test. Let the starter app download and install it.\n\n"
        + instructions
    )
    return {
        "START_VERSION": start,
        "UPDATE_VERSION": update,
        "START_TAG": start_tag,
        "UPDATE_TAG": update_tag,
    }


if __name__ == "__main__":
    values = prepare(
        Path.cwd(),
        os.environ["GITHUB_REPOSITORY"],
        os.environ["GITHUB_RUN_ID"],
        os.environ["GITHUB_RUN_ATTEMPT"],
    )
    with open(os.environ["GITHUB_ENV"], "a") as output:
        for key, value in values.items():
            output.write(f"{key}={value}\n")
            print(f"{key}={value}")
