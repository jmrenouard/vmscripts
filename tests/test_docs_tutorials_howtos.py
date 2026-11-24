"""Executable tests for vmscripts docs, tutorials, shell/Python scripts, and Mermaid."""

from __future__ import annotations

import json
import os
import pathlib
import py_compile
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

try:
    import yaml
except ImportError:  # pragma: no cover - optional in bare stdlib environments
    yaml = None

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCS_DIR = REPO_ROOT / "docs"

REQUIRED_QUADRANTS = (
    "01-tutorials",
    "02-how-to-guides",
    "03-reference",
    "04-explanation",
)

FENCE_OPEN_RE = re.compile(r"^([ \t]*)(`{3,}|~{3,})([^\n]*)$")
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)\n]+)\)")
HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*$")
MERMAID_HEADER_RE = re.compile(
    r"^(?:graph|flowchart|sequenceDiagram|classDiagram|stateDiagram(?:-v2)?|"
    r"erDiagram|gantt|pie|gitGraph)\b"
)


def _iter_repo_markdown() -> list[pathlib.Path]:
    """Return all unique Markdown files in the repository."""
    ignored = {".git", ".vagrant", "__pycache__", "node_modules"}
    files: list[pathlib.Path] = []
    for path in sorted(REPO_ROOT.rglob("*.md")):
        if any(part in ignored for part in path.parts):
            continue
        files.append(path)
    return files


def _extract_fenced_blocks(text: str) -> list[tuple[int, str, str, str]]:
    """Return (start_line, indent, lang, body) for each fenced block."""
    blocks: list[tuple[int, str, str, str]] = []
    lines = text.splitlines()
    idx = 0
    while idx < len(lines):
        match = FENCE_OPEN_RE.match(lines[idx])
        if not match:
            idx += 1
            continue
        indent, marker, info = match.groups()
        fence_char = marker[0]
        fence_len = len(marker)
        start_line = idx + 1
        lang = info.strip().split()[0].lower() if info.strip() else ""
        body_lines: list[str] = []
        idx += 1
        close_re = re.compile(rf"^\s*{re.escape(fence_char)}{{{fence_len},}}\s*$")
        while idx < len(lines) and not close_re.match(lines[idx]):
            body_lines.append(lines[idx])
            idx += 1
        blocks.append((start_line, indent, lang, "\n".join(body_lines)))
        idx += 1
    return blocks


def _strip_fences_and_code(text: str) -> list[tuple[int, str]]:
    """Return 1-based (lineno, line) outside fenced blocks with inline code stripped."""
    out: list[tuple[int, str]] = []
    in_fence = False
    fence_char = ""
    fence_len = 0
    for lineno, raw in enumerate(text.splitlines(), start=1):
        if in_fence:
            if re.match(rf"^\s*{re.escape(fence_char)}{{{fence_len},}}\s*$", raw):
                in_fence = False
            continue
        match = FENCE_OPEN_RE.match(raw)
        if match:
            marker = match.group(2)
            fence_char = marker[0]
            fence_len = len(marker)
            in_fence = True
            continue
        out.append((lineno, re.sub(r"`[^`]+`", " ", raw)))
    return out


def _usable_bash() -> str | None:
    """Return a native POSIX bash path usable for script syntax and source checks."""
    if os.name == "nt":
        return None
    return shutil.which("bash")


class TestScriptsSyntaxAndGenerators(unittest.TestCase):
    """Validate syntax across all shell/Python/JSON/YAML assets and generators."""

    def test_all_shell_scripts_pass_bash_n(self) -> None:
        """Run bash -n on every shell script in the repository on POSIX hosts."""
        bash_bin = _usable_bash()
        if bash_bin is None:
            self.skipTest("POSIX bash required for shell syntax and sourcing checks.")
        scripts = sorted(REPO_ROOT.rglob("*.sh"))
        self.assertGreaterEqual(len(scripts), 25)
        failures: list[str] = []
        for script in scripts:
            res = subprocess.run(
                [bash_bin, "-n", str(script)],
                capture_output=True,
                text=True,
                check=False,
            )
            if res.returncode != 0:
                failures.append(f"{script.relative_to(REPO_ROOT)}: {res.stderr.strip()}")
        self.assertEqual(failures, [], "\n".join(failures))

    def test_shell_libraries_source_cleanly(self) -> None:
        """Source docker.sh, vagrant.sh, and linode.sh and verify core functions."""
        bash_bin = _usable_bash()
        if bash_bin is None:
            self.skipTest("POSIX bash required for shell library sourcing.")

        checks = [
            "source ./docker.sh && declare -f dfrom dbash >/dev/null",
            (
                f"export VMS_DIR='{REPO_ROOT / 'vms'}' && "
                "source ./vagrant.sh && "
                "declare -f vlist vstart vstop vdelete vgenInventory vssh_exec >/dev/null"
            ),
            (
                "source ./linode.sh && "
                "declare -f llist lcreate ldelete lgenInventory lssh >/dev/null"
            ),
        ]
        for snippet in checks:
            res = subprocess.run(
                [bash_bin, "-c", snippet],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(res.returncode, 0, f"Failed '{snippet}': {res.stderr}")

    def test_all_python_scripts_compile(self) -> None:
        """Compile all Python scripts into a temporary directory without bytecode pollution."""
        py_files = sorted(REPO_ROOT.rglob("*.py"))
        self.assertGreaterEqual(len(py_files), 9)
        with tempfile.TemporaryDirectory() as tmpdir:
            for idx, py_file in enumerate(py_files):
                cfile = pathlib.Path(tmpdir) / f"mod_{idx}.pyc"
                py_compile.compile(str(py_file), cfile=str(cfile), doraise=True)

    def test_json_and_compose_yaml_parse(self) -> None:
        """Parse vm-vagrant/server.json and Docker Compose YAML files."""
        server_json = REPO_ROOT / "vm-vagrant" / "server.json"
        data = json.loads(server_json.read_text(encoding="utf-8"))
        self.assertIn("Vms", data)
        self.assertIn("node1", data["Vms"])
        for vm_cfg in data["Vms"].values():
            for key in ("distro", "prefix", "nbcpu", "ram", "enabled"):
                self.assertIn(key, vm_cfg)

        if yaml is not None:
            for rel in (
                "docker/galera/docker-compose.yaml",
                "docker/replication/docker-compose.yml",
            ):
                parsed = yaml.safe_load((REPO_ROOT / rel).read_text(encoding="utf-8"))
                self.assertIsInstance(parsed, dict, rel)

    def test_executable_tutorial_generators_in_sandbox(self) -> None:
        """Execute vms/ and linode/ Python generators inside a temporary directory."""
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        bash_bin = _usable_bash()

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = pathlib.Path(tmpdir)

            # 1. Execute vms/mygenconf.py with isolated output path
            out_vf = tmp / "Vagrantfile.test"
            vms_env = env.copy()
            vms_env["PYTHONPATH"] = str(REPO_ROOT / "vms")
            res_conf = subprocess.run(
                [
                    sys.executable,
                    str(REPO_ROOT / "vms" / "mygenconf.py"),
                    f"output={out_vf}",
                    "vm_number=2",
                    "vm_name_prefix=tut",
                    "vm_ram=512",
                ],
                cwd=tmp,
                env=vms_env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(res_conf.returncode, 0, res_conf.stderr)
            vf_text = out_vf.read_text(encoding="utf-8")
            self.assertIn('config.vm.define "tut1"', vf_text)
            self.assertIn('config.vm.define "tut2"', vf_text)
            self.assertIn("192.168.33.171", vf_text)
            self.assertIn('vb.memory = "512"', vf_text)

            # 2. Execute vms/mygenscript.py into temp cwd (uses default integer vm_number=5)
            res_scr = subprocess.run(
                [
                    sys.executable,
                    str(REPO_ROOT / "vms" / "mygenscript.py"),
                    "vm_name_prefix=tut",
                ],
                cwd=tmp,
                env=vms_env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(res_scr.returncode, 0, res_scr.stderr)
            inv_text = (tmp / "inventory").read_text(encoding="utf-8")
            self.assertIn("[control]", inv_text)
            self.assertIn("[target]", inv_text)
            self.assertIn("tut2", inv_text)
            self.assertIn("tut5", inv_text)
            self.assertTrue((tmp / "putty_tut1.bat").is_file())
            self.assertTrue((tmp / "putty_tut5.bat").is_file())

            # 3. Execute linode/mygenconf.py into temp cwd (uses defaults_elk nb_linode_vms=3)
            lin_env = env.copy()
            lin_env["PYTHONPATH"] = str(REPO_ROOT / "linode")
            res_lin = subprocess.run(
                [
                    sys.executable,
                    str(REPO_ROOT / "linode" / "mygenconf.py"),
                    "generic_prefix=demo",
                ],
                cwd=tmp,
                env=lin_env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(res_lin.returncode, 0, res_lin.stderr)
            gen_sh = tmp / "demo_generate_linodes.sh"
            drop_sh = tmp / "demo_drop_linodes.sh"
            self.assertIn("lcreate demo_elksrv", gen_sh.read_text(encoding="utf-8"))
            self.assertIn("ldelete demo_pgsrv1", drop_sh.read_text(encoding="utf-8"))
            self.assertIn("ldelete demo_pgsrv2", drop_sh.read_text(encoding="utf-8"))

            if bash_bin is not None:
                for generated in (gen_sh, drop_sh):
                    chk = subprocess.run(
                        [bash_bin, "-n", str(generated)],
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    self.assertEqual(chk.returncode, 0, chk.stderr)


class TestDocsTargetsAndDiataxis(unittest.TestCase):
    """Validate Make target references, Diataxis boundaries, STE, links, and Mermaid."""

    @staticmethod
    def _parse_make_targets(makefile_path: pathlib.Path) -> set[str]:
        targets: set[str] = set()
        for line in makefile_path.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^([A-Za-z0-9_.-]+):(?:\s|$)", line)
            if m and not m.group(1).startswith("."):
                targets.add(m.group(1))
        return targets

    def test_documented_scripts_and_make_targets_exist(self) -> None:
        """Verify documented repo scripts and Make targets actually exist."""
        required_files = (
            "profile",
            "vagrant.sh",
            "docker.sh",
            "linode.sh",
            "installSoft.sh",
            "installSoft2.sh",
            "installSoft_ubuntu.sh",
            "vms/init_vagrant.sh",
            "vms/start.sh",
            "vms/stop.sh",
            "vms/destroy.sh",
            "vms/status.sh",
            "vms/info.sh",
            "vms/genSshConfig.sh",
            "vms/mygenconf.py",
            "vms/mygenscript.py",
            "vm-vagrant/Makefile",
            "vm-vagrant/server.json",
            "docker/Makefile",
            "docker/Dockerfile",
            "docker/galera/docker-compose.yaml",
            "docker/replication/docker-compose.yml",
            "linode/mygenscript.py",
            "lxd/docker_iptables.sh",
        )
        for rel in required_files:
            self.assertTrue((REPO_ROOT / rel).is_file(), f"Missing documented file: {rel}")

        all_targets = self._parse_make_targets(
            REPO_ROOT / "docker" / "Makefile"
        ) | self._parse_make_targets(REPO_ROOT / "vm-vagrant" / "Makefile")

        missing_targets: list[str] = []
        for md_file in _iter_repo_markdown():
            text = md_file.read_text(encoding="utf-8")
            for m in re.finditer(r"\bmake\s+([A-Za-z0-9_-]+)\b", text):
                target = m.group(1)
                if target not in all_targets:
                    missing_targets.append(f"{md_file.relative_to(REPO_ROOT)}: make {target}")
        self.assertEqual(missing_targets, [], "\n".join(missing_targets))

    def test_diataxis_structure_and_quadrant_boundaries(self) -> None:
        """Verify docs/index.md, 4 quadrants, and genre separation rules."""
        self.assertTrue((DOCS_DIR / "index.md").is_file())
        for quadrant in REQUIRED_QUADRANTS:
            q_dir = DOCS_DIR / quadrant
            self.assertTrue(q_dir.is_dir(), f"Missing {quadrant}")
            self.assertTrue((q_dir / "index.md").is_file(), f"Missing {quadrant}/index.md")
            non_index = [p for p in q_dir.rglob("*.md") if p.name.lower() != "index.md"]
            self.assertTrue(non_index, f"Expected non-index pages in {quadrant}")

        for md_file in sorted(DOCS_DIR.rglob("*.md")):
            if md_file.name.lower() == "index.md":
                continue
            rel = md_file.relative_to(DOCS_DIR)
            if len(rel.parts) < 2:
                continue
            quadrant = rel.parts[0]
            lines = _strip_fences_and_code(md_file.read_text(encoding="utf-8"))
            body = "\n".join(line for _, line in lines)
            headings = [
                m.group(1) for _, line in lines if (m := HEADING_RE.match(line)) is not None
            ]

            if quadrant == "02-how-to-guides":
                self.assertRegex(body, re.compile(r"\b(?:validat|verif)\w*\b", re.I))
                self.assertRegex(body, re.compile(r"\b(?:rollback|revert|backout)\b", re.I))
                theory_re = re.compile(r"\b(?:why|architecture|theory|explanation)\b", re.I)
                self.assertFalse(any(theory_re.search(h) for h in headings), str(md_file))
            elif quadrant == "03-reference":
                self.assertTrue("|" in body or re.search(r"^\s*[-*]\s+", body, re.M))
                self.assertNotRegex(
                    body, re.compile(r"\b(?:in this tutorial|let's|step 1)\b", re.I)
                )
            elif quadrant == "04-explanation":
                proc_re = re.compile(r"\b(?:step\s+\d+|rollback|prerequisites)\b", re.I)
                self.assertFalse(any(proc_re.search(h) for h in headings), str(md_file))

    def test_how_to_guides_asd_ste100_constraints(self) -> None:
        """Enforce ASD-STE100 structural rules on docs/02-how-to-guides/*.md."""
        howto_dir = DOCS_DIR / "02-how-to-guides"
        for md_file in sorted(howto_dir.rglob("*.md")):
            text = md_file.read_text(encoding="utf-8")
            for lineno, line in _strip_fences_and_code(text):
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                self.assertNotIn(";", stripped, f"Semicolon in {md_file}:{lineno}")
                self.assertNotRegex(
                    stripped,
                    re.compile(r"\b(?:should|would|may|might|shall)\b", re.I),
                    f"Weak modal in {md_file}:{lineno}",
                )
                self.assertNotRegex(
                    stripped,
                    re.compile(r"\b[A-Za-z]+(?:n't|'re|'ve|'ll|'d)\b", re.I),
                    f"Contraction in {md_file}:{lineno}",
                )
                clean = re.sub(r"^\s*(?:[-*]|\d+\.)\s+", "", stripped)
                clean = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", clean)
                for sentence in re.split(r"(?<=[.!?])\s+", clean):
                    words = [w for w in re.split(r"\s+", sentence.strip()) if w]
                    if words:
                        self.assertLessEqual(
                            len(words),
                            20,
                            f"Sentence > 20 words in {md_file}:{lineno}: {sentence}",
                        )

    def test_relative_links_mermaid_ascii_and_english_isolation(self) -> None:
        """Verify relative links, zero ASCII diagrams, valid Mermaid, and English isolation."""
        broken: list[str] = []
        diagram_errors: list[str] = []
        mermaid_blocks: list[tuple[str, str]] = []
        fr_re = re.compile(
            r"\b(?:préparation|paramétrage|sécurisation|ajout des|tutoriel|avertissement|étapes)\b",
            re.I,
        )

        for md_file in _iter_repo_markdown():
            rel = md_file.relative_to(REPO_ROOT).as_posix()
            text = md_file.read_text(encoding="utf-8")
            self.assertNotIn("dd4t.dadesktop.com", text, rel)
            self.assertNotIn("easymysql", text.lower(), rel)

            for lineno, line in _strip_fences_and_code(text):
                self.assertNotRegex(line, fr_re, f"French leakage in {rel}:{lineno}")
                for match in LINK_RE.finditer(line):
                    raw_dest = match.group(1).strip()
                    target = raw_dest.split("#", 1)[0].split("?", 1)[0].strip()
                    if not target or target.startswith(("http://", "https://", "mailto:", "#")):
                        continue
                    if not (md_file.parent / target).resolve().exists():
                        broken.append(f"{rel}:{lineno}: {target}")

            for start_line, indent, lang, body in _extract_fenced_blocks(text):
                if lang == "mermaid":
                    if indent:
                        diagram_errors.append(f"{rel}:{start_line}: indented mermaid fence")
                    header = next(
                        (
                            ln.strip()
                            for ln in body.splitlines()
                            if ln.strip() and not ln.strip().startswith("%%")
                        ),
                        "",
                    )
                    if not MERMAID_HEADER_RE.match(header):
                        diagram_errors.append(f"{rel}:{start_line}: bad header '{header}'")
                    mermaid_blocks.append((f"{rel}:{start_line}", body))
                elif not lang or lang in {"bash", "sh", "shell"}:
                    if re.search(r"[┌┐└┘├┤┬┴┼─│═║╔╗╚╝]|-->|<--", body):
                        diagram_errors.append(
                            f"{rel}:{start_line}: ASCII arrow/box in '{lang or 'untagged'}'"
                        )

        self.assertEqual(broken, [], "\n".join(broken))
        self.assertTrue(mermaid_blocks, "Expected Mermaid diagrams in documentation")
        self.assertEqual(diagram_errors, [], "\n".join(diagram_errors))

        mmdc_bin = shutil.which("mmdc")
        if mmdc_bin is not None:
            with tempfile.TemporaryDirectory() as tmpdir:
                out_svg = pathlib.Path(tmpdir) / "rendered.svg"
                for loc, code in mermaid_blocks:
                    res = subprocess.run(
                        [mmdc_bin, "-i", "-", "-o", str(out_svg)],
                        input=code,
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    self.assertEqual(res.returncode, 0, f"mmdc failed on {loc}: {res.stderr}")


if __name__ == "__main__":
    unittest.main()
