# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-06-02

### Added
- Created 1-click automatic Render Blueprint deployment configuration (`render.yaml`).
- Implemented widescreen PowerPoint presentation deck (`JalRakshak_Project_Presentation.pptx`).
- Merged upstream feature repository (`suryateja2109/jalshanak`) keeping custom modifications.
- Added project health files (`.editorconfig`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `.env.example`).
- Added Spec-Kit intents layer (`.specify/constitution.md` and `specs/`).

### Fixed
- Resolved passlib / bcrypt incompatibility causing `ValueError: password cannot be longer than 72 bytes` during database seeding.
- Corrected static site `VITE_API_BASE_URL` env variable routing in Render blueprints.
