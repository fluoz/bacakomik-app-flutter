from pathlib import Path
import tempfile
import unittest

from prepare_rpm_update_test import prepare


class RpmUpdateTestPreparation(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "pubspec.yaml").write_text("version: 2.18.0+40\n")
        self.variables = self.root / "lib/core/constants/variables.dart"
        self.variables.parent.mkdir(parents=True)
        self.original = (
            "static const String githubRepo = 'sofyan-rs/yoru-comic-app';\n"
            "static const String latestReleaseApi =\n"
            "    'https://api.github.com/repos/$githubRepo/releases/latest';\n"
        )
        self.variables.write_text(self.original)

    def test_two_versions_and_exact_prerelease_endpoint(self):
        values = prepare(self.root, "fluoz/bacakomik-app-flutter", "123", "1")
        self.assertEqual(values["START_VERSION"], "2.18.1")
        self.assertEqual(values["UPDATE_VERSION"], "2.18.2")
        self.assertFalse(values["START_TAG"].startswith("v"))
        self.assertIn(f'/releases/tags/{values["UPDATE_TAG"]}', self.variables.read_text())
        self.assertIn("githubRepo = 'sofyan-rs/yoru-comic-app'", self.variables.read_text())
        self.assertEqual((self.root / "pubspec.yaml").read_text(), "version: 2.18.0+40\n")
        summary = (self.root / ".rpm-update-test/summary.md").read_text()
        self.assertIn("administrator prompt", summary)
        self.assertIn("2.18.1", summary)
        self.assertIn("2.18.2", summary)

    def test_cannot_prepare_for_upstream(self):
        with self.assertRaises(ValueError):
            prepare(self.root, "sofyan-rs/yoru-comic-app", "123", "1")
        self.assertEqual(self.variables.read_text(), self.original)

    def test_invalid_run_identifiers_are_rejected(self):
        with self.assertRaises(ValueError):
            prepare(self.root, "fluoz/bacakomik-app-flutter", "123\nOTHER=value", "1")
        self.assertEqual(self.variables.read_text(), self.original)

    def test_retry_gets_unique_tags(self):
        first = prepare(self.root, "fluoz/bacakomik-app-flutter", "123", "1")
        second = prepare(self.root, "fluoz/bacakomik-app-flutter", "123", "2")
        self.assertNotEqual(first["START_TAG"], second["START_TAG"])
        self.assertNotEqual(first["UPDATE_TAG"], second["UPDATE_TAG"])


if __name__ == "__main__":
    unittest.main()
