import argparse
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from second_brain import (
    check_brain,
    command_archive_tasks,
    command_new_process,
    command_new_project,
    command_upgrade,
    initialize_brain,
)


class SecondBrainTests(unittest.TestCase):
    def setUp(self):
        self.print_patcher = patch("builtins.print")
        self.print_patcher.start()
        self.addCleanup(self.print_patcher.stop)
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "brain"

    def tearDown(self):
        self.temp.cleanup()

    def errors(self):
        return [finding for finding in check_brain(self.root) if finding.level == "ERROR"]

    def test_fresh_brain_is_valid(self):
        initialize_brain(self.root)
        self.assertEqual([], self.errors())

    def test_initialization_preserves_custom_working_style(self):
        initialize_brain(self.root)
        working_style = self.root / "workflow/working-style.md"
        working_style.write_text("custom content\n", encoding="utf-8")

        initialize_brain(self.root)

        self.assertEqual("custom content\n", working_style.read_text(encoding="utf-8"))

    def test_broken_link_is_reported(self):
        initialize_brain(self.root)
        note = self.root / "knowledge/note.md"
        note.write_text(
            "---\ntitle: Note\ndescription: Note\ntype: note\n---\n\n"
            "[Missing](missing.md)\n",
            encoding="utf-8",
        )
        messages = [finding.message for finding in self.errors()]
        self.assertTrue(any("broken link" in message for message in messages))

    def test_completed_open_item_is_reported(self):
        initialize_brain(self.root)
        project = self.root / "projects/example"
        project.mkdir()
        (project / "project.md").write_text(
            "---\ntitle: Example\ndescription: Example\ntype: project\n"
            "repo: git@example.test:org/example.git\n---\n\n# Example\n\n"
            "## Open items\n\n- [x] Finished\n",
            encoding="utf-8",
        )
        messages = [finding.message for finding in self.errors()]
        self.assertIn("completed task found under 'Open items'", messages)

    def test_invalid_frontmatter_is_reported(self):
        initialize_brain(self.root)
        note = self.root / "knowledge/broken.md"
        note.write_text("---\ntitle: [broken\n---\n", encoding="utf-8")
        messages = [finding.message for finding in self.errors()]
        self.assertTrue(any("invalid YAML" in message for message in messages))

    def test_non_mapping_schema_is_reported(self):
        initialize_brain(self.root)
        (self.root / "second-brain.yml").write_text("- invalid\n", encoding="utf-8")
        messages = [finding.message for finding in self.errors()]
        self.assertIn("schema configuration must be a mapping", messages)

    def test_secret_like_value_is_reported(self):
        initialize_brain(self.root)
        note = self.root / "knowledge/unsafe.md"
        note.write_text(
            "---\ntitle: Unsafe\ndescription: Unsafe test\ntype: note\n---\n\n"
            "Token: ghp_abcdefghijklmnopqrstuvwxyz123456\n",
            encoding="utf-8",
        )
        messages = [finding.message for finding in self.errors()]
        self.assertTrue(any("possible secret" in message for message in messages))

    def test_invalid_calendar_values_in_log_are_reported(self):
        initialize_brain(self.root)
        project = self.root / "projects/example"
        project.mkdir()
        (project / "project.md").write_text(
            "---\ntitle: Example\ndescription: Example\ntype: project\n"
            "path: /tmp/example\n---\n\n# Example\n",
            encoding="utf-8",
        )
        (project / "log.md").write_text(
            "## 2026-W99\n\n- 2026-02-31: Impossible date.\n",
            encoding="utf-8",
        )
        messages = [finding.message for finding in self.errors()]
        self.assertTrue(any("invalid ISO-week" in message for message in messages))
        self.assertTrue(any("invalid dated log" in message for message in messages))

    def test_project_process_and_archive_workflow(self):
        initialize_brain(self.root)
        result = command_new_project(
            argparse.Namespace(
                name="sample-app",
                title="Sample App",
                description=None,
                repo="git@example.test:org/sample-app.git",
                local_path=None,
                path=str(self.root),
            )
        )
        self.assertEqual(0, result)

        result = command_new_process(
            argparse.Namespace(
                project="sample-app",
                name="deploy",
                trigger="Deploy the application",
                title="Deploy",
                description=None,
                path=str(self.root),
            )
        )
        self.assertEqual(0, result)

        project = self.root / "projects/sample-app/project.md"
        project.write_text(
            project.read_text(encoding="utf-8") + "\n- [x] Ship the first release\n",
            encoding="utf-8",
        )
        result = command_archive_tasks(
            argparse.Namespace(project="sample-app", path=str(self.root))
        )
        self.assertEqual(0, result)

        self.assertNotIn("[x]", project.read_text(encoding="utf-8"))
        archive = self.root / "projects/sample-app/completed-items.md"
        self.assertIn("Ship the first release", archive.read_text(encoding="utf-8"))
        self.assertIn("completed-items.md", project.read_text(encoding="utf-8"))
        router = self.root / "projects/sample-app/processes.md"
        self.assertIn("processes/deploy.md", router.read_text(encoding="utf-8"))
        self.assertEqual([], self.errors())

    def test_upgrade_reports_and_backs_up_changed_managed_file(self):
        initialize_brain(self.root)
        agents = self.root / "AGENTS.md"
        agents.write_text("custom managed content\n", encoding="utf-8")

        self.assertEqual(
            1,
            command_upgrade(argparse.Namespace(path=str(self.root), check=True)),
        )
        self.assertEqual(
            0,
            command_upgrade(argparse.Namespace(path=str(self.root), check=False)),
        )

        self.assertNotEqual("custom managed content\n", agents.read_text(encoding="utf-8"))
        backups = list((self.root / ".backups").rglob("AGENTS.md"))
        self.assertEqual(1, len(backups))
        self.assertEqual("custom managed content\n", backups[0].read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
