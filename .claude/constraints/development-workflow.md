# Development Workflow

> Read this file when: Starting new feature development, creating PRs, or need workflow guidance

---

## 🔴 MANDATORY: Branch → PR → CodeRabbit → Merge

**直接提交到 main 分支是严格禁止的！**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   main ─── 🚫 DIRECT COMMIT FORBIDDEN 🚫                               │
│                                                                         │
│   CORRECT FLOW:                                                         │
│                                                                         │
│   feature/xxx ──▶ PR ──▶ CodeRabbit Review ──▶ Merge ──▶ main         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Complete Flow

```
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│ 1.Require│──▶│ 2.Design │──▶│ 3.Develop│──▶│ 4.Test   │──▶│ 5.Release│
│  Issue   │   │  Review  │   │  Code    │   │  Verify  │   │  Deploy  │
└──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘
     │              │              │              │              │
     ▼              ▼              ▼              ▼              ▼
  gh issue       P0/P1必       feature/       PR +         release.sh
  --template     须设计        分支开发       CodeRabbit
```

---

## Stage 1: Requirement (Issue)

```bash
# Create issue with template
gh issue create --template 01_feature_request.md  # New feature
gh issue create --template 02_bug_report.md       # Bug fix
gh issue create --template 03_task.md             # Task
```

**Required fields**:
- Priority (P0-P3)
- Acceptance criteria
- Documentation requirements

---

## Stage 2: Design Review

| Priority | Requirement |
|----------|-------------|
| P0 | MUST write design document |
| P1 | MUST write design document or detailed comment |
| P2/P3 | Optional |

---

## Stage 3: Development

### 🔴 MANDATORY: Feature Branch Workflow

**NEVER commit directly to main branch!**

```bash
# ❌ FORBIDDEN
git checkout main
git commit -m "feat: something"
git push origin main

# ✅ REQUIRED
git checkout -b feature/xxx
git commit -m "feat: something"
git push origin feature/xxx
gh pr create --title "feat: something" --body "..."
```

### Branch Naming
```
feature/xxx    # New feature
fix/xxx        # Bug fix
hotfix/xxx     # P0 urgent fix
refactor/xxx   # Refactoring
```

### Commit Convention
```
feat:     New feature
fix:      Bug fix
docs:     Documentation
style:    Code format
refactor: Refactoring
test:     Tests
chore:    Build/tools
```

### Complete PR Flow
```bash
# 1. Create feature branch from main
git checkout main
git pull
git checkout -b feature/redis-cache

# 2. Develop and commit
# develop...
git add .
git commit -m "feat: implement Redis cache layer"

# 3. Push to remote
git push -u origin feature/redis-cache

# 4. Create Pull Request
gh pr create --title "feat: Redis缓存层实现" --body "$(cat <<'EOF'
## Summary
- Implement Redis cache service with async operations
- Add caching to contents API (5-15 min TTL)
- Add caching to search API (5-10 min TTL)

## Test plan
- [ ] Verify cache hit/miss behavior
- [ ] Test cache invalidation
- [ ] Measure performance improvement
EOF
)"

# 5. Wait for CodeRabbit review (automatic)

# 6. Address review comments if any

# 7. Merge after approval
gh pr merge --squash
```

---

## Stage 4: Testing & CodeRabbit Review

### 🔴 MANDATORY: CodeRabbit Review Required

**PR merge is BLOCKED until CodeRabbit completes review!**

```
PR Created ──▶ CodeRabbit Reviews ──▶ Address Comments ──▶ Merge
                  │
                  └── 🚫 Cannot merge until review complete
```

### Local Checks
```bash
# Run checklist
./scripts/checklist.sh
```

**Requirements**:
- Unit tests for core modules
- Integration tests for API endpoints
- Manual testing for UI

### CodeRabbit Auto Review
- **Automatic**: CodeRabbit reviews all PRs automatically
- **Config**: `.coderabbit.yaml`
- **Blocking**: Must wait for review before merging

### CodeRabbit Status Check
```bash
# Check PR status
gh pr view <pr-number>

# Check CodeRabbit review status
gh pr checks <pr-number>
```

### When Manual Review Required
CodeRabbit may fail to review in these cases:
- Invalid configuration
- API quota exceeded
- Critical system errors

**Notification**: Email sent automatically when CodeRabbit fails critically

### Merge Checklist
- [ ] CodeRabbit review completed
- [ ] All review comments addressed
- [ ] CI/CD checks passed
- [ ] At least 1 approval (if required)
- [ ] Ready to merge

---

## Stage 5: Release

```bash
./scripts/release.sh patch "Fix bug"    # v1.0.0 → v1.0.1
./scripts/release.sh minor "New feat"   # v1.0.0 → v1.1.0
./scripts/release.sh major "Breaking"   # v1.0.0 → v2.0.0
```

---

## Priority Definitions

| Level | Definition | Response |
|-------|------------|----------|
| P0 | Critical/Blocking | Immediately |
| P1 | High | Within sprint |
| P2 | Normal | Next sprint |
| P3 | Low | When available |
