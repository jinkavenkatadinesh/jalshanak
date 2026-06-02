# 🤖 AGENTS.md — AI & Agent Orchestration Guidelines

This repository is optimized for agentic software engineering. Any AI agent or developer assisting in this workspace must follow these guidelines.

---

## 🛠️ Execution Scopes & Allowed Tools

1. **Workspace Scope**: All file operations, command executions, and builds must be run inside the project root directory (`d:\jalshanak\`).
2. **Database Fallbacks**: Standard fallback is SQLite (`sqlite:///./jalrakshak.db`) for zero-config sandboxed local testing. Production deploys use PostgreSQL.
3. **Allowed Hashing / Encryption**: Use standard passlib + bcrypt. Intercept length constraints (>72 bytes) cleanly using the monkey-patch implemented in `app/auth.py`.

---

## 🔒 Security & Secrets Protection

- **DO NOT commit `.env` files** containing live database credentials, production secret keys, or SSH keys.
- Always use `.env.example` as a template for environment configuration.
- Perform pre-commit checks to catch accidental secret leakage.

---

## 🧠 Spec-Driven Development

This repository enforces spec-driven development. 
- Refer to the project intent layer in `.specify/constitution.md` before starting implementation.
- All new features must have a corresponding specification written inside the `specs/` directory before writing code.
