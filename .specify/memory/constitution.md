# Spec-Driven Development Constitution

This document acts as the core intent layer for the **JalRakshak** repository. All changes and features must comply with the principles outlined below.

---

## 🏛️ Core Principles

1. **AI-Friendly Codebase**: Keep structures clear, maintain descriptive names, and preserve `AGENTS.md` and inline docstrings.
2. **Robust Hashing**: Password storage must use bcrypt + passlib. Any 72-byte truncation issues must be handled gracefully at runtime by the patch in `auth.py`.
3. **Dual Database Architecture**: SQLite for zero-config sandbox and local development testing, and PostgreSQL for live containerized production deployment.
4. **Comprehensive Checks**: All code modifications must pass Ruff linting, Mypy type-checking, and coverage tests in the CI/CD pipeline.
