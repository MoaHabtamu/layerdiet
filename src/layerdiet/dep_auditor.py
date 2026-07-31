"""Audits declared Python dependencies against actual source code imports."""

import ast
import os
import re
from dataclasses import dataclass
from typing import Set, List, Dict


@dataclass
class DependencyAuditResult:
    declared_dependencies: Set[str]
    used_dependencies: Set[str]
    unused_dependencies: Set[str]


def extract_imports_from_file(file_path: str) -> Set[str]:
    imports = set()
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            tree = ast.parse(f.read(), filename=file_path)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        top = alias.name.split(".")[0]
                        imports.add(top.lower().replace("-", "_"))
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        top = node.module.split(".")[0]
                        imports.add(top.lower().replace("-", "_"))
    except Exception:
        pass
    return imports


def extract_project_imports(directory: str) -> Set[str]:
    all_imports = set()
    for root, _, files in os.walk(directory):
        if any(ignored in root for ignored in (".venv", "venv", ".git", "build", "dist")):
            continue
        for f in files:
            if f.endswith(".py"):
                all_imports.update(extract_imports_from_file(os.path.join(root, f)))
    return all_imports


def parse_requirements_file(file_path: str) -> Set[str]:
    deps = set()
    if not os.path.isfile(file_path):
        return deps
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("-"):
                continue
            pkg = re.split(r"[><=~!;]", line)[0].strip()
            if pkg:
                deps.add(pkg.lower().replace("-", "_"))
    return deps


class DependencyAuditor:
    @staticmethod
    def audit(project_dir: str, requirements_file: str = "requirements.txt") -> DependencyAuditResult:
        req_path = os.path.join(project_dir, requirements_file) if not os.path.isabs(requirements_file) else requirements_file
        declared = parse_requirements_file(req_path)
        used = extract_project_imports(project_dir)

        unused = {d for d in declared if d not in used}
        return DependencyAuditResult(
            declared_dependencies=declared,
            used_dependencies=used,
            unused_dependencies=unused
        )
