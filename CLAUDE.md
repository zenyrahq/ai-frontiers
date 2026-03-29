# AI Frontiers - Project Instructions

> **Read this file at session start.** For detailed constraints, see `.claude/constraints/`

---

## Project Overview

**AI Frontiers** - AI news aggregation platform collecting research papers, blog posts, and open-source projects.

- **Repo**: https://github.com/zenyrahq/ai-frontiers
- **Stack**: Python (FastAPI), TypeScript (Next.js), PostgreSQL, Redis, Docker
- **Status**: MVP completed, optimization phase

---

## 🔴 Red Lines (Never Violate)

| # | Rule |
|---|------|
| 1 | **Docs MUST be updated** after feature completion → `.claude/constraints/documentation-rules.md` |
| 2 | **Comments MUST be in English** → `.claude/constraints/code-quality.md` |
| 3 | **SonarQube compliant** - No BLOCKER/CRITICAL/MAJOR/MINOR |
| 4 | **Private info** in `docs-private/`, never upload to GitHub |
| 5 | **Production** uses `docker-compose.prod.yml` |

---

## 📋 Constraint Files (Read When Needed)

| Trigger | Read |
|---------|------|
| Starting development / Creating PRs | `.claude/constraints/development-workflow.md` |
| After feature completion | `.claude/constraints/documentation-rules.md` |
| Writing / reviewing code | `.claude/constraints/code-quality.md` |
| Git branch / commit / PR | `.claude/constraints/git-conventions.md` |
| Creating releases | `.claude/constraints/release-process.md` |

---

## ⚡ Quick Commands

```bash
# Create issue
gh issue create --template 01_feature_request.md

# Run checklist
./scripts/checklist.sh

# Release
./scripts/release.sh patch "Fix bug"

# Deploy
docker compose -f docker-compose.prod.yml up -d --build
```

---

## 🤖 CodeRabbit (Auto Review)

- **Auto-review**: All PRs reviewed automatically
- **Config**: `.coderabbit.yaml`
- **Manual review**: Only when CodeRabbit fails critically
- **Notification**: Email sent automatically on failure

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `CLAUDE.md` | This file |
| `.claude/constraints/` | Detailed constraints |
| `docs/api.md` | API reference |
| `docs/architecture.md` | System architecture |
| `docs-private/project-management/` | PM docs (private) |

---

## 🚨 Session Checklist

**Start of session**:
- [ ] Read this file
- [ ] Check `docs-private/project-management/PROJECT_MANAGEMENT.md` for status

**After significant feature**:
- [ ] Run `./scripts/checklist.sh`
- [ ] Read `.claude/constraints/documentation-rules.md`
- [ ] Update relevant docs

---

**Last Updated**: 2026-03-29
