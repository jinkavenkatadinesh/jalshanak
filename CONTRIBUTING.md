# Contributing to JalRakshak

Thank you for your interest in contributing to **JalRakshak**! As a CivicTech platform dedicated to municipal transparency, we maintain high standards of code hygiene, UI/UX consistency, and testing.

This guide outlines our development workflow, styling regulations, and pull request procedures.

---

## 🏛️ Code Architecture Guidelines

We divide this codebase strictly into `backend` (FastAPI services) and `frontend` (Vite + React.js SPA). 

### 🐍 Backend Guidelines (FastAPI & SQLAlchemy)
1. **Type Annotations**: All function signatures must have type annotations (e.g., `db: Session`, `user_id: int`).
2. **PEP 8 Compliance**: Follow standard Python style guidelines. Keep code clean and self-documenting.
3. **Pydantic Validation**: Never decode requests directly. Always construct schemas in `schemas.py` for request validation and output modeling.
4. **Database Operations**: Do not perform direct raw SQL execution. Always use SQLAlchemy's ORM model query structures to ensure portability between PostgreSQL and SQLite engines.

### ⚛️ Frontend Guidelines (Vite & React)
1. **Vanilla CSS Design System**:
   * All styles must inherit from the custom variables declared in `frontend/src/index.css`.
   * **Do not use Tailwind CSS** or write inline ad-hoc styles in components. Use standard flexbox/grid classes and the custom variables (e.g., `var(--primary)`, `var(--bg-glass)`).
   * Maintain the Hydric dark-ocean theme across all viewports.
2. **Leaflet Map Integration**:
   * Dynamic markers must use `L.divIcon` to bypass Vite image bundling path issues.
   * Encapsulate zoom controls and coordinates recentering safely inside subcomponents using leaflet hooks (like `useMap`).
3. **API Integrity**:
   * Always route network requests through the customized `api.js` Axios client to leverage JWT header interceptors and global 401 expiration redirections.

---

## 🚦 Branching and Git Workflow

We adopt a standard GitHub Flow model for codebase integration:

1. **Fork the Repository**: Clone your fork locally.
2. **Create a Feature Branch**: Use descriptive prefixes:
   * `feat/add-notification-bell` (for new features)
   * `fix/gps-null-exception` (for bug fixes)
   * `docs/update-manual` (for documentation)
3. **Commit often**: Write clear, imperative-style commit messages (e.g., `feat: integrate proximity duplicate scan algorithm`).
4. **Push & Pull Request**: Submit a Pull Request targeting the `main` branch.

---

## 🧪 Testing Requirements

To keep JalRakshak production-ready:
* **Backend validation**: Verify that `uvicorn app.main:app` starts successfully with no import errors, and check `/docs` to ensure Swagger schemas are generated correctly.
* **Frontend validation**: Execute `npm run build` inside `frontend/` to confirm that all JSX compiles successfully and there are no bundler warnings.
* **Database tests**: Ensure that starting the system with `DATABASE_URL` omitted successfully initializes the zero-config SQLite `jalrakshak.db` file.
