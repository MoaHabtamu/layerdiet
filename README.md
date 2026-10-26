# 🐳 LayerDiet

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)]()
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**LayerDiet** is an automated CLI auditor and optimizer that slims down bloated Python container images. It pinpoints caching anti-patterns, finds unimported packages in `requirements.txt`, and generates high-efficiency multi-stage Dockerfiles.

---

## ⚡ Highlights

- **Dockerfile Layer Linting**: Detects missing `--no-cache-dir`, uncleaned apt lists, heavy full-size base images, and cache invalidation anti-patterns.
- **Dead Dependency Detection**: Statically traces `import` statements across your codebase and contrasts them against declared dependencies in `requirements.txt`.
- **Multi-Stage Generator**: One-command conversion to a production-ready multi-stage build running as a non-root user.
- **Zero Heavy Dependencies**: Pure standard library implementation with zero external runtime requirements.

---

## 🚀 Quickstart

### Installation

```bash
git clone https://github.com/MoaHabtamu/layerdiet.git
cd layerdiet
pip install -e .
```

### CLI Usage

#### 1. Audit Dockerfile & Dependencies
```bash
layerdiet audit ./my-project
```

Output:
```text
==============================================================
         🐳 LayerDiet - Container & Dependency Audit
==============================================================

⚠️  Found 2 Dockerfile Anti-Pattern(s):
  [HIGH] Line 4: Pip installed packages without '--no-cache-dir'.
      💡 Recommendation: Add '--no-cache-dir' to pip install to avoid saving wheels in the image layer.
  [MEDIUM] Line 1: Heavy base image detected: 'python:3.11'.
      💡 Recommendation: Use 'python:3.x-slim' or 'python:3.x-alpine' to reduce image footprint by ~700MB.

📦 Unused Dependencies in Manifest (1):
  • boto3 (installed but never imported in source)
```

#### 2. Generate Optimized Multi-Stage Dockerfile
```bash
layerdiet optimize --python 3.12 --output Dockerfile.slim
```

---

## 🧪 Running Tests

```bash
python3 -m unittest discover tests
```

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
