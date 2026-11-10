# Manual RPM update test

This branch is for testing only. Keep its workflow and test endpoint out of the
upstream PR. The production branch continues to use upstream releases.

In the fork, open **Actions → Release → Run workflow**, select
`test/rpm-in-app-update`, and run it. The existing `release.yml` path is reused so
the workflow can be dispatched from this branch without changing the default
branch. The run itself is named **RPM update test**.

One run builds two RPMs and publishes two prereleases in the fork. With the
current base version 2.18.0, they are:

- Starter: 2.18.1, to download and install manually.
- Target: 2.18.2, to install through the app's Update button.

Each tag includes the run ID and attempt. Neither release is marked latest.
The target is published and its GitHub SHA-256 digest checked before the starter
is published. Both RPMs are built with the target's exact release API endpoint;
prereleases are therefore usable without changing the production latest release.

After the run succeeds, its summary and release notes contain the Fedora steps.
Install the starter, run `/usr/bin/yoru`, open **More → Check for updates**, and
cancel the administrator prompt once to check recovery. Retry and approve it;
confirm DNF completes, the app restarts, and the displayed version and `rpm -q yoru`
both report the target version. A final check should find no newer update.

These are regular Yoru RPMs using the normal app data. If repeating a test after
the target is installed, use `sudo dnf downgrade ./Yoru-2.18.1-linux-x86_64.rpm`
to install the starter again. To return to a production RPM with a lower version,
use `dnf downgrade` with that RPM. Deleting the prereleases alone does not change
the endpoint embedded in a test build.
