#!/usr/bin/env python3
"""Regresiones ejecutables para los invariantes semanticos del linter."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LINTER = REPO / "tools" / "lint_siege.py"


class LintRegressionTests(unittest.TestCase):
    maxDiff = None

    def run_lint(self, root: Path, project: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(LINTER), str(root), project],
            cwd=REPO,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )

    def injected_case(
        self,
        project_dir: str,
        project_arg: str,
        relative_file: str,
        old: str,
        new: str,
        expected: str,
    ) -> None:
        with tempfile.TemporaryDirectory(prefix="aoe2-lint-") as tmp:
            root = Path(tmp)
            (root / "reference").symlink_to(REPO / "reference", target_is_directory=True)
            shutil.copytree(REPO / project_dir, root / project_dir)
            path = root / relative_file
            source = path.read_text(encoding="utf-8")
            self.assertIn(old, source, f"fixture desactualizada: falta {old!r}")
            path.write_text(source.replace(old, new, 1), encoding="utf-8")

            result = self.run_lint(root, project_arg)
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertIn(expected, result.stdout)

    def test_clean_projects(self) -> None:
        for project in ("siege", "forty", "semiUtils"):
            with self.subTest(project=project):
                result = self.run_lint(REPO, project)
                self.assertEqual(result.returncode, 0, result.stdout)

    def test_rejects_vanilla_goal_for_point_pair(self) -> None:
        self.injected_case(
            "siege", "siege", "siege/siege/const.per",
            "(defconst gl-pt1 100)", "(defconst gl-pt1 20)",
            "up-get-point usa goal gl-pt1=20",
        )

    def test_rejects_vanilla_goal_for_search_state(self) -> None:
        self.injected_case(
            "siege", "siege", "siege/siege/const.per",
            "(defconst gl-local-total 102)", "(defconst gl-local-total 30)",
            "up-get-search-state usa goal gl-local-total=30",
        )

    def test_rejects_unbound_rule_variable(self) -> None:
        self.injected_case(
            "siege", "siege", "siege/siege/combat.per",
            "(up-find-player enemy find-closest gl-temp)",
            "(up-get-player-fact this-any-enemy player-number 0 gl-temp)",
            "usa this-any-enemy sin enlazar any-enemy",
        )

    def test_rejects_rule_variable_in_fact(self) -> None:
        self.injected_case(
            "semiUtils", "semiUtils", "semiUtils/semiutils.per",
            "    (taunt-detected any-computer 201)\n",
            "    (taunt-detected any-computer 201)\n"
            "    (stance-toward this-any-computer neutral)\n",
            "this-any-computer como hecho",
        )

    def test_rejects_closed_state_machine(self) -> None:
        self.injected_case(
            "forty", "forty", "forty/forty.per",
            "\t(set-goal gl-mode m-grow)\n", "",
            "gl-mode: maquina de estado sin entrada",
        )

    def test_requires_wall_placement_setup(self) -> None:
        self.injected_case(
            "semiUtils", "semiUtils", "semiUtils/semiutils.per",
            "    (enable-wall-placement 1)\n", "",
            "build-wall/build-gate sin enable-wall-placement",
        )

    def test_rejects_duplicate_rule(self) -> None:
        rule = """(defrule
    (gold-amount > 1500)
    (players-population any-ally > 20)
=>
    (tribute-to-player this-any-ally gold 100)
)
"""
        self.injected_case(
            "semiUtils", "semiUtils", "semiUtils/semiutils.per",
            rule, rule + "\n" + rule,
            "duplicada exactamente",
        )

    def test_unknown_project_does_not_fall_back_to_siege(self) -> None:
        result = self.run_lint(REPO, "typo")
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertIn("Proyecto desconocido", result.stdout)


if __name__ == "__main__":
    unittest.main()
