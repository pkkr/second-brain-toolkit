import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from connect_neurons import generate


PROJECT = """---
title: Test Project
description: Test project
type: project
repo: git@example.test:org/project.git
status: active
---

# Test Project
"""

NOTE = """---
title: Test Note
description: Test note
type: note
---

# Test Note
"""


class GeneratorTests(unittest.TestCase):
    def setUp(self):
        self.print_patcher = patch("builtins.print")
        self.print_patcher.start()
        self.addCleanup(self.print_patcher.stop)
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        project = self.root / "projects/test-project"
        project.mkdir(parents=True)
        (project / "project.md").write_text(PROJECT, encoding="utf-8")
        (project / "log.md").write_text(
            "## 2026-W29\n\n- 2026-07-14: Released a test outcome.\n",
            encoding="utf-8",
        )
        knowledge = self.root / "knowledge"
        knowledge.mkdir()
        (knowledge / "note.md").write_text(NOTE, encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def test_generate_is_idempotent(self):
        self.assertTrue(generate(self.root))
        self.assertFalse(generate(self.root))
        self.assertTrue((self.root / "index.md").exists())
        self.assertTrue((self.root / "log/2026-W29.md").exists())

    def test_check_mode_detects_drift_without_writing(self):
        generate(self.root)
        index = self.root / "knowledge/index.md"
        original = index.read_text(encoding="utf-8")
        (self.root / "knowledge/another.md").write_text(
            NOTE.replace("Test Note", "Another Note"), encoding="utf-8"
        )

        self.assertTrue(generate(self.root, check=True))
        self.assertEqual(original, index.read_text(encoding="utf-8"))

    def test_private_directory_is_ignored(self):
        private = self.root / "private"
        private.mkdir()
        (private / "secret.md").write_text(NOTE, encoding="utf-8")

        generate(self.root)

        self.assertFalse((private / "index.md").exists())
        self.assertNotIn("private/", (self.root / "index.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
