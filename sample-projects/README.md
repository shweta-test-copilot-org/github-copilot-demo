# 🎯 Choose Your Sample Project

This lab provides **brownfield sample projects** that simulate real enterprise codebases. Choose the language/stack you're most comfortable with.

---

## Available Projects

| Project | Language | Stack | Lines of Code | Status |
|---------|----------|-------|---------------|--------|
| [contoso-orders-python](./contoso-orders-python/) | Python 3.11 | FastAPI, Pydantic, structlog | ~2,500 | ✅ **Available** |
| contoso-orders-typescript | TypeScript | Express/NestJS | ~2,000 | 🔜 Coming Soon |
| contoso-orders-java | Java 17 | Spring Boot | ~2,500 | 🔜 Coming Soon |
| contoso-orders-csharp | C# | ASP.NET Core | ~2,500 | 🔜 Coming Soon |

> **Tip**: If your preferred language isn't available yet, use **contoso-orders-python**—the concepts transfer to any stack.

---

## Brownfield Characteristics

All sample projects share these **realistic enterprise constraints**:

### 🔒 Legacy Authentication

```python
# legacy/auth_provider.py
# DO NOT MODIFY - Migration to OAuth planned for Q3
# This module is used by 47 services across 12 teams
```

Every project has a legacy auth module that **must not be changed**—just like real enterprise codebases.

### 📋 Existing Patterns

- Specific error handling conventions
- Custom logging approaches
- Team-standard naming conventions
- Legacy dependencies that can't be upgraded

### 🧪 Intentional Test Gaps

- Some modules have tests, others don't
- This is deliberate—**you'll generate the missing tests** during Exercise 3

### 📁 Mixed Code Quality

- Some areas are well-documented
- Others have minimal comments
- Some follow patterns, others are ad-hoc

---

## Quick Start: Python

```bash
# Navigate to the sample project
cd sample-projects/contoso-orders-python

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
uvicorn src.main:app --reload

# Run existing tests
pytest tests/
```

**Health check**: `curl http://localhost:8000/health`

---

## What You'll Build

During the lab, you'll create VS Code Copilot customization primitives that work with these brownfield codebases.

All files go in `.github/` at the **repository root** (not inside the sample project folder).
