import argparse
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from second_brain import (
    check_brain,
    command_archive_tasks,
    command_migrate_legacy,
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

    def test_config_validation_can_be_skipped_for_non_vault_content(self):
        self.root.mkdir()
        (self.root / "note.md").write_text(
            "---\ntitle: Note\ndescription: Note\ntype: note\n---\n",
            encoding="utf-8",
        )

        findings = check_brain(
            self.root,
            include_generated=False,
            include_config=False,
        )

        self.assertEqual([], findings)

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

    def test_legacy_migration_standardizes_structure_and_preserves_prose(self):
        project = self.root / "projekte/sample"
        processes = project / "prozesse"
        workflow = self.root / "workflow"
        processes.mkdir(parents=True)
        workflow.mkdir(parents=True)
        (self.root / "AGENTS.md").write_text("legacy rules\n", encoding="utf-8")
        (self.root / "README.md").write_text("legacy readme\n", encoding="utf-8")
        (self.root / "inbox.md").write_text("# Inbox\n", encoding="utf-8")
        (self.root / "connect_neurons.py").write_text("legacy tool\n", encoding="utf-8")
        (self.root / "requirements.txt").write_text("pyyaml\n", encoding="utf-8")
        (self.root / "setup.sh").write_text("legacy setup\n", encoding="utf-8")
        (project / "projekt.md").write_text(
            "---\ntitle: Beispiel\ndescription: Deutscher Inhalt\ntype: project\n"
            "repo: git@example.test:org/sample.git\npfad: ~/code/sample\nstatus: aktiv\n---\n\n"
            "# Beispiel\n\n## Ziel\n\nDeutsche Fachtexte bleiben erhalten.\n\n"
            "## Stack & Architektur\n\nDetails.\n\n## Entscheidungen\n\nKeine.\n\n"
            "## Offene Themen\n\n- [ ] Aufgabe\n",
            encoding="utf-8",
        )
        (project / "prozesse.md").write_text(
            "---\ntitle: Prozesse\ndescription: Router\ntype: guide\n---\n\n# Prozesse\n\n"
            "| Auslöser | Prozess | Zuletzt geprüft |\n|---|---|---|\n"
            "| Deploy | [Deploy](prozesse/deploy.md) | 2026-07-14 |\n",
            encoding="utf-8",
        )
        (processes / "deploy.md").write_text(
            "---\ntitle: Deploy\ndescription: Exakter Ablauf\ntype: guide\n---\n\n"
            "# Deploy\n\n1. `deploy --exact`\n",
            encoding="utf-8",
        )
        (workflow / "vorgehen.md").write_text(
            "---\ntitle: Vorgehen\ndescription: Persönliche Regeln\ntype: guide\n---\n\n"
            "# Vorgehen\n\nDeutsch als Arbeitssprache.\n",
            encoding="utf-8",
        )
        (self.root / "index.md").write_text("# stale\n", encoding="utf-8")

        dry_run = argparse.Namespace(
            path=str(self.root),
            apply=False,
            allow_dirty=False,
            remove_legacy_tools=True,
        )
        self.assertEqual(0, command_migrate_legacy(dry_run))
        self.assertTrue((project / "projekt.md").exists())

        apply = argparse.Namespace(
            path=str(self.root),
            apply=True,
            allow_dirty=False,
            remove_legacy_tools=True,
        )
        self.assertEqual(0, command_migrate_legacy(apply))

        migrated = self.root / "projects/sample/project.md"
        text = migrated.read_text(encoding="utf-8")
        self.assertIn("path: ~/code/sample", text)
        self.assertIn("status: active", text)
        self.assertIn("## Open items", text)
        self.assertIn("Deutsche Fachtexte bleiben erhalten.", text)
        self.assertTrue((self.root / "projects/sample/processes/deploy.md").exists())
        self.assertIn(
            "processes/deploy.md",
            (self.root / "projects/sample/processes.md").read_text(encoding="utf-8"),
        )
        self.assertIn(
            "Deutsch als Arbeitssprache.",
            (self.root / "workflow/working-style.md").read_text(encoding="utf-8"),
        )
        self.assertFalse((self.root / "connect_neurons.py").exists())
        self.assertTrue(list((self.root / ".backups").rglob("connect_neurons.py")))
        self.assertIn(".backups/", (self.root / ".gitignore").read_text(encoding="utf-8"))
        self.assertEqual([], self.errors())

    def test_legacy_migration_refuses_dirty_git_worktree(self):
        legacy = self.root / "projekte/sample"
        legacy.mkdir(parents=True)
        marker = legacy / "projekt.md"
        marker.write_text("tracked\n", encoding="utf-8")
        subprocess.run(
            ["git", "init", "-b", "main", str(self.root)],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "-C", str(self.root), "config", "user.email", "test@example.test"],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(self.root), "config", "user.name", "Test User"],
            check=True,
        )
        subprocess.run(["git", "-C", str(self.root), "add", "."], check=True)
        subprocess.run(
            ["git", "-C", str(self.root), "commit", "-m", "fixture"],
            check=True,
            capture_output=True,
        )
        marker.write_text("dirty\n", encoding="utf-8")

        result = command_migrate_legacy(
            argparse.Namespace(
                path=str(self.root),
                apply=True,
                allow_dirty=False,
                remove_legacy_tools=False,
            )
        )

        self.assertEqual(1, result)
        self.assertTrue((self.root / "projekte").exists())
        self.assertFalse((self.root / "projects").exists())


if __name__ == "__main__":
    unittest.main()
