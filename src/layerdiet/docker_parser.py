"""Dockerfile instruction parser and AST representation."""

import re
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class DockerInstruction:
    instruction: str  # FROM, RUN, COPY, ADD, etc.
    arguments: str
    line_number: int
    raw: str


class DockerfileParser:
    @staticmethod
    def parse_file(file_path: str) -> List[DockerInstruction]:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            return DockerfileParser.parse_string(f.read())

    @staticmethod
    def parse_string(content: str) -> List[DockerInstruction]:
        instructions: List[DockerInstruction] = []
        lines = content.splitlines()

        current_inst: Optional[str] = None
        current_args: List[str] = []
        start_line = 0
        raw_accum: List[str] = []

        for idx, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            # Check if this line is continuation
            is_continuation = stripped.endswith("\\")
            line_body = stripped[:-1].strip() if is_continuation else stripped

            if current_inst is None:
                # Expect new instruction
                parts = line_body.split(None, 1)
                cmd = parts[0].upper()
                args = parts[1] if len(parts) > 1 else ""
                current_inst = cmd
                current_args = [args]
                start_line = idx
                raw_accum = [line]
            else:
                current_args.append(line_body)
                raw_accum.append(line)

            if not is_continuation:
                instructions.append(DockerInstruction(
                    instruction=current_inst,
                    arguments=" ".join(current_args),
                    line_number=start_line,
                    raw="\n".join(raw_accum)
                ))
                current_inst = None
                current_args = []
                raw_accum = []

        return instructions
