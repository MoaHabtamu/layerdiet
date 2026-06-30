"""Detects layer bloat, caching anti-patterns, and uncleaned build caches."""

from dataclasses import dataclass
from typing import List
from layerdiet.docker_parser import DockerInstruction


@dataclass
class AntiPatternFinding:
    severity: str  # HIGH, MEDIUM, LOW
    rule_id: str
    message: str
    line_number: int
    recommendation: str


class DockerLinter:
    @staticmethod
    def audit(instructions: List[DockerInstruction]) -> List[AntiPatternFinding]:
        findings: List[AntiPatternFinding] = []

        has_multi_stage = sum(1 for inst in instructions if inst.instruction == "FROM") > 1
        pip_installs = [inst for inst in instructions if inst.instruction == "RUN" and "pip install" in inst.arguments]
        copy_instructions = [inst for inst in instructions if inst.instruction in ("COPY", "ADD")]

        for inst in instructions:
            # 1. Base image bloat check
            if inst.instruction == "FROM":
                base = inst.arguments.split()[0].lower()
                if "python:" in base and not any(tag in base for tag in ("slim", "alpine")):
                    findings.append(AntiPatternFinding(
                        severity="MEDIUM",
                        rule_id="HEAVY_BASE_IMAGE",
                        message=f"Heavy base image detected: '{base}'.",
                        line_number=inst.line_number,
                        recommendation="Use 'python:3.x-slim' or 'python:3.x-alpine' to reduce image footprint by ~700MB."
                    ))

            # 2. RUN pip install without --no-cache-dir
            if inst.instruction == "RUN" and "pip install" in inst.arguments:
                if "--no-cache-dir" not in inst.arguments:
                    findings.append(AntiPatternFinding(
                        severity="HIGH",
                        rule_id="PIP_CACHE_BLOAT",
                        message="Pip installed packages without '--no-cache-dir'.",
                        line_number=inst.line_number,
                        recommendation="Add '--no-cache-dir' to pip install to avoid saving wheels in the image layer."
                    ))

            # 3. apt-get install without cleaning /var/lib/apt/lists
            if inst.instruction == "RUN" and "apt-get install" in inst.arguments:
                if "/var/lib/apt/lists" not in inst.arguments or "rm -rf" not in inst.arguments:
                    findings.append(AntiPatternFinding(
                        severity="HIGH",
                        rule_id="APT_LISTS_BLOAT",
                        message="apt-get install executed without purging '/var/lib/apt/lists/*'.",
                        line_number=inst.line_number,
                        recommendation="Append '&& rm -rf /var/lib/apt/lists/*' in the same RUN layer to reclaim 50-100MB."
                    ))

        # 4. Cache bust: COPY . before pip install
        if pip_installs and copy_instructions:
            first_pip_line = pip_installs[0].line_number
            for cp in copy_instructions:
                if cp.line_number < first_pip_line and (cp.arguments.startswith(". .") or cp.arguments.startswith("./ .")):
                    findings.append(AntiPatternFinding(
                        severity="HIGH",
                        rule_id="CACHE_INVALIDATION_RISK",
                        message="COPY . . executed before running 'pip install'.",
                        line_number=cp.line_number,
                        recommendation="Copy only 'requirements.txt' or 'pyproject.toml' first, run pip install, then COPY source code."
                    ))
                    break

        # 5. Multi-stage pattern check
        if not has_multi_stage and len(pip_installs) > 0:
            findings.append(AntiPatternFinding(
                severity="LOW",
                rule_id="SINGLE_STAGE_BUILD",
                message="Dockerfile uses a single build stage.",
                line_number=1,
                recommendation="Adopt a multi-stage build to isolate compilers (gcc, build-essential) from final runtime image."
            ))

        return findings
