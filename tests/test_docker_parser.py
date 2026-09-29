import sys
import os
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from layerdiet.docker_parser import DockerfileParser


class TestDockerParser(unittest.TestCase):
    def test_parse_multiline(self):
        sample = """
FROM python:3.11-slim
RUN apt-get update && \\
    apt-get install -y curl && \\
    rm -rf /var/lib/apt/lists/*
COPY . /app
"""
        instructions = DockerfileParser.parse_string(sample)
        self.assertEqual(len(instructions), 3)
        self.assertEqual(instructions[0].instruction, "FROM")
        self.assertEqual(instructions[1].instruction, "RUN")
        self.assertIn("rm -rf /var/lib/apt/lists/*", instructions[1].arguments)


if __name__ == "__main__":
    unittest.main()
