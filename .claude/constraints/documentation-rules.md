# Documentation Rules

> Read this file when: Completing a feature, updating docs, or need documentation guidance

---

## 🔴 RED LINE: Document Directory Classification

**Rule**: All documents MUST be placed in the correct directory based on their type.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     Document Directory Classification                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  📂 docs/                        → Public (Upload to GitHub)                │
│     ├── Technical docs          → API, Architecture, Deployment            │
│     ├── Design docs             → System design, Technical decisions       │
│     └── Development docs        → Guides, References                       │
│                                                                              │
│  📂 docs-private/                → Private (NEVER upload to GitHub)         │
│     ├── Project management      → PM handbook, Plans, Roadmaps             │
│     ├── Claude configuration    → Claude config guides                     │
│     └── User-specified files    → Any file user specifies as private       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Document Classification Rules

### 📂 docs/ (Public - Upload to GitHub)

| Document Type | Examples | Location |
|---------------|----------|----------|
| API Documentation | API endpoints, request/response | `docs/api.md` |
| Architecture | System design, components | `docs/architecture.md` |
| Deployment | Server setup, Docker config | `docs/DEPLOYMENT_COMPLETE_GUIDE.md` |
| Release | Release process, changelog | `docs/RELEASE_PROCESS.md` |
| Development | Setup guide, conventions | `docs/QUICKSTART.md` |
| Technical Reports | Crawler, NLP, Search reports | `docs/*_REPORT.md` |

### 📂 docs-private/ (Private - NEVER Upload)

| Document Type | Examples | Location |
|---------------|----------|----------|
| Project Management | Handbook, KPIs, progress | `docs-private/project-management/` |
| Optimization Plans | Performance, quality plans | `docs-private/project-management/OPTIMIZATION_PLAN.md` |
| Extension Roadmap | Future features, timeline | `docs-private/project-management/EXTENSION_ROADMAP.md` |
| Claude Configuration | Claude config guide | `docs-private/CLAUDE_CONFIG_GUIDE.md` |
| Sensitive Info | IPs, passwords, secrets | `docs-private/` (root or subdirs) |
| User-specified | Any file user marks private | `docs-private/` |

---

## ⚠️ MANDATORY: Update Docs After Feature Completion

This is a **long-term project**. Documentation is critical for sustainability.

---

## When to Update

| Trigger | Document | Directory |
|---------|----------|-----------|
| New API endpoint | `docs/api.md` | `docs/` |
| Architecture change | `docs/architecture.md` | `docs/` |
| Database schema change | `docs/architecture.md` | `docs/` |
| Deployment config change | `docs/DEPLOYMENT_COMPLETE_GUIDE.md` | `docs/` |
| Feature completion | `PROJECT_MANAGEMENT.md` | `docs-private/project-management/` |
| Optimization task | `OPTIMIZATION_PLAN.md` | `docs-private/project-management/` |
| New feature planning | `EXTENSION_ROADMAP.md` | `docs-private/project-management/` |
| Claude config change | `CLAUDE_CONFIG_GUIDE.md` | `docs-private/` |

---

## Complete Documentation Structure

```
ai-frontiers/
│
├── docs/                                    # 📂 PUBLIC (GitHub)
│   ├── api.md                               # API reference
│   ├── architecture.md                      # System architecture
│   ├── RELEASE_PROCESS.md                   # Release guide
│   ├── DEPLOYMENT_COMPLETE_GUIDE.md         # Deployment guide
│   ├── QUICKSTART.md                        # Quick start
│   ├── PROJECT.md                           # Project overview
│   │
│   └── (Technical Reports)
│       ├── ARXIV_CRAWLER_REPORT.md
│       ├── NLP_PROCESSOR_REPORT.md
│       ├── SEARCH_SERVICE_REPORT.md
│       └── FRONTEND_REPORT.md
│
└── docs-private/                            # 📂 PRIVATE (NOT GitHub)
    │
    ├── project-management/
    │   ├── PROJECT_MANAGEMENT.md            # Project handbook
    │   ├── OPTIMIZATION_PLAN.md             # Optimization plan
    │   └── EXTENSION_ROADMAP.md             # Future roadmap
    │
    ├── CLAUDE_CONFIG_GUIDE.md               # Claude configuration guide
    │
    └── (Sensitive Documents)
        ├── SERVER_SETUP_COMMANDS.md         # Server IPs, commands
        ├── INFRASTRUCTURE_TEST_REPORT.md    # Test results with IPs
        └── DEPLOYMENT_COMPLETE_GUIDE.md     # Deployment with secrets
```

---

## Self-Check After Completion

```
- [ ] Is this a significant feature? (not one-line fix)
- [ ] Architecture doc needs update?         → docs/architecture.md
- [ ] API doc needs new endpoint?            → docs/api.md
- [ ] Project management needs progress?     → docs-private/project-management/
- [ ] Is this document PRIVATE?              → docs-private/

If ANY answer is YES → UPDATE THE CORRECT DOCUMENT
```

---

## How to Mark a Document as Private

1. **User specifies**: "This file should be private"
2. **Contains sensitive info**: IPs, passwords, secrets, personal data
3. **Action**: Move to `docs-private/` directory

```bash
# Move public doc to private
mv docs/sensitive-file.md docs-private/
```

---

## Document Templates

### API Endpoint (docs/api.md)
```markdown
### GET /v1/xxx

**Description**: Brief description

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| id | int | Yes | Resource ID |

**Response**:
\`\`\`json
{
  "id": 1,
  "name": "example"
}
\`\`\`

**Status Codes**:
- 200: Success
- 404: Not found
```

### Architecture Change (docs/architecture.md)
```markdown
## Component Name

**Purpose**: What it does

**Dependencies**: What it depends on

**Interfaces**: How to interact with it

**Design Decisions**: Why it's designed this way
```

### Project Management Update (docs-private/project-management/)
```markdown
## [Date] Update

**Completed**:
- [ ] Task 1
- [ ] Task 2

**In Progress**:
- [ ] Task 3

**Notes**:
- Important decisions or blockers
```
