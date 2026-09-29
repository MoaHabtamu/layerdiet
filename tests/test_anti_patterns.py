import sys
import os
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from layerdiet.docker_parser import DockerfileParser
from layerdiet.anti_patterns import DockerLinter


class TestAntiPatterns(unittest.TestCase):
    def test_detects_pip_no_cache_missing(self):
        sample = """
FROM python:3.11
RUN pip install requests
"""
        instructions = DockerfileParser.parse_string(sample)
        findings = DockerLinter.audit(instructions)
        rule_ids = {f.rule_id for f in findings}
        self.assertIn("PIP_CACHE_BLOAT", rule_ids)
        self.assertIn("HEAVY_BASE_IMAGE", rule_ids)


if __name__ == "__main__":
    unittest.main()
